from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Iterable

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
import oracledb

# --- Connection IDs (ajuste conforme cadastrados no Airflow) ---
ORACLE_CONN_ID_RAW = "oracle_raw"
ORACLE_CONN_ID_TRUSTED = "oracle_trusted"

# --- Tabela destino (TRUSTED) ---
TARGET_TABLE = "CLICHES"

# Colunas existentes na TRUSTED
TRUSTED_COLS = [
    "CODCLICHE",
    "FORNECEDOR",
    "MODULO",
    "FIGURA",
    "STATUS",
    "PRECO",
    "IDCLIENTE",
    "DESATIVADOSN",
    "DATACRIACAOREGISTRO",
]


def _make_oracle_conn(conn_id: str):
    c = BaseHook.get_connection(conn_id)
    extra = c.extra_dejson or {}
    port = c.port or 1521
    service_name = extra.get("service_name")
    sid = extra.get("sid")
    if service_name:
        dsn = oracledb.makedsn(c.host, port, service_name=service_name)
    elif sid:
        dsn = oracledb.makedsn(c.host, port, sid=sid)
    else:
        # fallback: usar schema como service_name
        dsn = oracledb.makedsn(c.host, port, service_name=c.schema)
    return oracledb.connect(user=c.login, password=c.password, dsn=dsn)


def _chunk(iterable: Iterable[Dict[str, Any]], size: int) -> Iterable[List[Dict[str, Any]]]:
    batch: List[Dict[str, Any]] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def etl_cliches_raw_to_trusted(**context):
    # 1) Extrai da RAW apenas as colunas que a TRUSTED possui
    select_sql = f"""
        SELECT
            CODCLICHE,
            FORNECEDOR,
            MODULO,
            FIGURA,
            STATUS,
            PRECO,
            IDCLIENTE,
            DESATIVADOSN,
            DATACRIACAOREGISTRO
        FROM {TARGET_TABLE}
    """

    raw_conn = _make_oracle_conn(ORACLE_CONN_ID_RAW)
    try:
        cur = raw_conn.cursor()
        cur.execute(select_sql)
        colnames = [d[0] for d in cur.description]  # nomes em UPPER
        rows = cur.fetchall()
    finally:
        raw_conn.close()

    if not rows:
        return

    # 2) Transforma → lista de dicionários (mantendo apenas colunas TRUSTED)
    payload = []
    for r in rows:
        as_dict = dict(zip(colnames, r))
        # garantir float para BINARY_DOUBLE; demais campos seguem como estão
        if as_dict.get("PRECO") is not None:
            as_dict["PRECO"] = float(as_dict["PRECO"])
        
        # Formatar DATACRIACAOREGISTRO para o formato YYYY/MM/DD HH:MM:SS.000
        if as_dict.get("DATACRIACAOREGISTRO") is not None:
            if isinstance(as_dict["DATACRIACAOREGISTRO"], datetime):
                as_dict["DATACRIACAOREGISTRO"] = as_dict["DATACRIACAOREGISTRO"].strftime('%Y/%m/%d %H:%M:%S.000')
        
        # filtra/extrai só as colunas da TRUSTED e mantém ordem estável
        payload.append({c: as_dict.get(c) for c in TRUSTED_COLS})

    # 3) MERGE na TRUSTED (idempotente por CODCLICHE)
    merge_sql = f"""
        MERGE INTO {TARGET_TABLE} t
        USING (
            SELECT
                :CODCLICHE CODCLICHE,
                :FORNECEDOR FORNECEDOR,
                :MODULO MODULO,
                :FIGURA FIGURA,
                :STATUS STATUS,
                :PRECO PRECO,
                :IDCLIENTE IDCLIENTE,
                :DESATIVADOSN DESATIVADOSN,
                TO_TIMESTAMP(:DATACRIACAOREGISTRO, 'YYYY/MM/DD HH24:MI:SS.FF3') AS DATACRIACAOREGISTRO
            FROM dual
        ) s
        ON (t.CODCLICHE = s.CODCLICHE)
        WHEN MATCHED THEN UPDATE SET
            t.FORNECEDOR          = s.FORNECEDOR,
            t.MODULO              = s.MODULO,
            t.FIGURA              = s.FIGURA,
            t.STATUS              = s.STATUS,
            t.PRECO               = s.PRECO,
            t.IDCLIENTE           = s.IDCLIENTE,
            t.DESATIVADOSN        = s.DESATIVADOSN,
            t.DATACRIACAOREGISTRO = s.DATACRIACAOREGISTRO
        WHEN NOT MATCHED THEN INSERT (
            {", ".join(TRUSTED_COLS)}
        ) VALUES (
            {", ".join("s."+c for c in TRUSTED_COLS)}
        )
    """

    trusted_conn = _make_oracle_conn(ORACLE_CONN_ID_TRUSTED)
    try:
        cur_t = trusted_conn.cursor()
        # executa em lotes para tabelas grandes
        for batch in _chunk(payload, size=1000):
            cur_t.executemany(merge_sql, batch)
        trusted_conn.commit()
    finally:
        trusted_conn.close()


with DAG(
    dag_id="etl_cliches_raw_to_trusted",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # se Airflow >= 2.4 pode usar schedule=None
    catchup=False,
    tags=["etl", "oracle", "cliches"],
):
    PythonOperator(
        task_id="merge_upsert_cliches",
        python_callable=etl_cliches_raw_to_trusted,
    )