from __future__ import annotations
from datetime import datetime, date
from typing import Any, Dict, List, Iterable, Set

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
import oracledb

# --- Connection IDs ---
ORACLE_CONN_ID_RAW = "oracle_raw"
ORACLE_CONN_ID_TRUSTED = "oracle_trusted"

# --- Tabelas ---
TABLE_NAME = "FACAS"  # nome simples; prefixe OWNER. se necessário

# Colunas que, se existirem, tratamos como BINARY_DOUBLE (cast para float)
BINARY_DOUBLE_CANDIDATES = {"PRECO", "REFUGOCLIENTE"}

# Colunas que, se existirem, tratamos como texto (cast para str)
VARCHAR_CANDIDATES = {
    "CODFACA", "DESCRTIPOFACA", "FORNECEDOR", "MODULO", "ARQUIVO",
    "LOCALIZACAO", "FIGURA", "OBS", "CODIGOERP"
}

def _make_oracle_conn(conn_id: str):
    c = BaseHook.get_connection(conn_id)
    extra = c.extra_dejson or {}
    port = c.port or 1521
    svc = extra.get("service_name")
    sid = extra.get("sid")
    if svc:
        dsn = oracledb.makedsn(c.host, port, service_name=svc)
    elif sid:
        dsn = oracledb.makedsn(c.host, port, sid=sid)
    else:
        dsn = oracledb.makedsn(c.host, port, service_name=c.schema)
    return oracledb.connect(user=c.login, password=c.password, dsn=dsn)

def _chunk(iterable: Iterable[Dict[str, Any]], size: int) -> Iterable[List[Dict[str, Any]]]:
    buf: List[Dict[str, Any]] = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf

def _char1(v: Any) -> str | None:
    if v is None:
        return None
    if v in (1, True, "1", "Y", "y"):
        return "Y"
    if v in (0, False, "0", "N", "n"):
        return "N"
    return str(v)[:1]

def _get_my_owner(conn) -> str:
    with conn.cursor() as cur:
        cur.execute("select user from dual")
        return cur.fetchone()[0]

def _get_table_cols(conn, owner: str, table: str) -> Set[str]:
    with conn.cursor() as cur:
        cur.execute("""
            select column_name
            from all_tab_columns
            where owner = :own and upper(table_name) = :tn
        """, {"own": owner.upper(), "tn": table.upper()})
        return {r[0].upper() for r in cur.fetchall()}

def etl_facas_raw_to_trusted(**context):
    # 1) Descobre colunas existentes em RAW e TRUSTED e toma a interseção
    raw_conn = _make_oracle_conn(ORACLE_CONN_ID_RAW)
    trusted_conn = _make_oracle_conn(ORACLE_CONN_ID_TRUSTED)
    try:
        raw_owner = _get_my_owner(raw_conn)
        trusted_owner = _get_my_owner(trusted_conn)
        raw_cols = _get_table_cols(raw_conn, raw_owner, TABLE_NAME)
        tr_cols  = _get_table_cols(trusted_conn, trusted_owner, TABLE_NAME)

        cols_to_use = sorted(raw_cols & tr_cols)
        if "CODFACA" not in cols_to_use:
            raise ValueError(f"A tabela {trusted_owner}.{TABLE_NAME} não possui a coluna chave CODFACA.")

        # 2) Extrai da RAW apenas as colunas que existem nas duas pontas
        select_sql = f"SELECT {', '.join(cols_to_use)} FROM {TABLE_NAME}"
        cur_raw = raw_conn.cursor()
        cur_raw.execute(select_sql)
        colnames = [d[0] for d in cur_raw.description]
        rows = cur_raw.fetchall()

        if not rows:
            return

        # 3) Transforma → coerção leve (float em BINARY_DOUBLE; str onde for texto; normaliza CHAR(1))
        payload: List[Dict[str, Any]] = []
        for r in rows:
            rec = dict(zip(colnames, r))

            # Se existir DESATIVADOSN, normaliza para 1 char
            if "DESATIVADOSN" in cols_to_use:
                rec["DESATIVADOSN"] = _char1(rec.get("DESATIVADOSN"))

            # Casts para float nas BINARY_DOUBLE conhecidas que existirem
            for c in (BINARY_DOUBLE_CANDIDATES & set(cols_to_use)):
                v = rec.get(c)
                if v is not None:
                    rec[c] = float(v) if isinstance(v, (int, float)) else float(str(v))

            # Opcional: força str nas candidatas VARCHAR que existirem (evita DPY-3013)
            for c in (VARCHAR_CANDIDATES & set(cols_to_use)):
                v = rec.get(c)
                rec[c] = None if v is None else str(v)
            
            # Formatar DATACRIACAOREGISTRO para o formato YYYY/MM/DD HH:MM:SS.000
            if "DATACRIACAOREGISTRO" in cols_to_use and rec.get("DATACRIACAOREGISTRO") is not None:
                if isinstance(rec["DATACRIACAOREGISTRO"], datetime):
                    rec["DATACRIACAOREGISTRO"] = rec["DATACRIACAOREGISTRO"].strftime('%Y/%m/%d %H:%M:%S.000')

            payload.append({c: rec.get(c) for c in cols_to_use})

        # 4) MERGE dinâmico com as colunas disponíveis
        using_select = ", ".join([f"TO_TIMESTAMP(:{c}, 'YYYY/MM/DD HH24:MI:SS.FF3') AS {c}" if c == "DATACRIACAOREGISTRO" else f":{c} {c}" for c in cols_to_use])
        set_lines = ", ".join([f"t.{c} = s.{c}" for c in cols_to_use if c != "CODFACA"])
        merge_sql = f"MERGE INTO {TABLE_NAME} t USING (SELECT {using_select} FROM dual) s ON (t.CODFACA = s.CODFACA) WHEN MATCHED THEN UPDATE SET {set_lines} WHEN NOT MATCHED THEN INSERT ({', '.join(cols_to_use)}) VALUES ({', '.join('s.'+c for c in cols_to_use)})"

        # 5) Carrega na TRUSTED em lotes
        cur_tr = trusted_conn.cursor()
        for batch in _chunk(payload, size=1000):
            cur_tr.executemany(merge_sql, batch)
        trusted_conn.commit()

    finally:
        try:
            raw_conn.close()
        finally:
            trusted_conn.close()

with DAG(
    dag_id="etl_facas_raw_to_trusted",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["etl", "oracle", "facas"],
):
    PythonOperator(
        task_id="merge_upsert_facas",
        python_callable=etl_facas_raw_to_trusted,
    )