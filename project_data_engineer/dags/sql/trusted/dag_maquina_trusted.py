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
TARGET_TABLE = "MAQUINA"

# Colunas existentes na TRUSTED (ordem preservada para INSERT)
TRUSTED_COLS = [
    "MAQ_ID",
    "MAQUINA",
    "NOMEMAQUINA",
    "TIPO",
    "CUSTOHORA",                 # BINARY_DOUBLE
    "UNIDPRODUTIVIDADE",
    "DESCUNIDPRODUTIVIDADE",
    "SETUP",
    "PRODM2",
    "PRODBATIDAS",
    "PRODKG",
    "PRODMAQUINA",
    "HOMENSTURMA",
    "GANTT",
    "NRDECORES",
    "IDGRUPOMAQUINA",
    "TAREFAATUAL",
    "INICIOTAREFAATUAL",
    "FIMPREVTAREFAATUAL",
    "PARADAATUAL",
    "INICIOPARADAATUAL",
    "PROGRAMARPRODUCAO",         # CHAR(1)
    "CODIGOERP",
    "PORCMINLARGURARESINADA",
    "CARGAMAQLOTE",
    "REFILEDIRETOPRENSA",        # CHAR(1)
    "DIFPORCPRODUTMAQFT_MENOS",
    "DIFPORCPRODUTMAQFT_MAIS",
    "PEDIDOMINIMOM2",
]

# Colunas BINARY_DOUBLE da TRUSTED para converter para float
BINARY_DOUBLE_COLS = {"CUSTOHORA"}

# Colunas TIMESTAMP da TRUSTED para formatar
TIMESTAMP_COLS = {"INICIOTAREFAATUAL", "FIMPREVTAREFAATUAL", "INICIOPARADAATUAL"}

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

def etl_maquina_raw_to_trusted(**context):
    # 1) Extrai da RAW apenas as colunas que a TRUSTED possui
    select_sql = f"SELECT {', '.join(TRUSTED_COLS)} FROM {TARGET_TABLE}"

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
    payload: List[Dict[str, Any]] = []
    for r in rows:
        rec = dict(zip(colnames, r))

        # Conversões leves: BINARY_DOUBLE -> float (quando não for None)
        for c in BINARY_DOUBLE_COLS:
            if rec.get(c) is not None:
                rec[c] = float(rec[c])

        # Formatar campos TIMESTAMP para o formato YYYY/MM/DD HH:MM:SS.000
        for c in TIMESTAMP_COLS:
            if c in rec and rec.get(c) is not None and isinstance(rec[c], datetime):
                rec[c] = rec[c].strftime('%Y/%m/%d %H:%M:%S.000')

        # Monta o registro final na ordem da TRUSTED
        payload.append({c: rec.get(c) for c in TRUSTED_COLS})

    # 3) MERGE na TRUSTED (idempotente por MAQ_ID)
    using_select = ", ".join([
        f"TO_TIMESTAMP(:{c}, 'YYYY/MM/DD HH24:MI:SS.FF3') AS {c}" if c in TIMESTAMP_COLS else f":{c} {c}" 
        for c in TRUSTED_COLS
    ])
    set_lines = ", ".join([f"t.{c} = s.{c}" for c in TRUSTED_COLS if c != "MAQ_ID"])

    merge_sql = f"MERGE INTO {TARGET_TABLE} t USING (SELECT {using_select} FROM dual) s ON (t.MAQ_ID = s.MAQ_ID) WHEN MATCHED THEN UPDATE SET {set_lines} WHEN NOT MATCHED THEN INSERT ({', '.join(TRUSTED_COLS)}) VALUES ({', '.join('s.'+c for c in TRUSTED_COLS)})"

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
    dag_id="etl_maquina_raw_to_trusted",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # se Airflow >= 2.4 pode usar schedule=None
    catchup=False,
    tags=["etl", "oracle", "maquina"],
):
    PythonOperator(
        task_id="merge_upsert_maquina",
        python_callable=etl_maquina_raw_to_trusted,
    )