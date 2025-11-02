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
TARGET_TABLE = "PARADAS"

# Colunas existentes na TRUSTED (ordem preservada para INSERT) — alinhadas ao DDL
TRUSTED_COLS = [
    "IDPARADA",
    "PARADA",
    "DESCRICAO",
    "SETOR",
    "TIPO",
    "USADAONDULADEIRA",
    "USADACONVERSAO",   # << NOVA
    "DESATIVADA",       # << NOVA
    "FLAGAJUSTE",       # << NOVA
    "FLAGEXTERNA",      # << NOVA
]

# Campos NOT NULL críticos para validarmos antes do MERGE (evita ORA-01400)
REQUIRED_NOT_NULL = {
    "IDPARADA",
    "PARADA",
    "USADAONDULADEIRA",
    "USADACONVERSAO",
    "DESATIVADA",
    "FLAGAJUSTE",
    "FLAGEXTERNA",
}

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

def etl_paradas_raw_to_trusted(**context):
    # 1) Extrai da RAW apenas as colunas que a TRUSTED possui
    select_sql = f"""
        SELECT
            {", ".join(TRUSTED_COLS)}
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

    # 2) Transforma → lista de dicionários (mantendo apenas colunas TRUSTED) + validações NOT NULL
    payload: List[Dict[str, Any]] = []
    skipped = 0
    for r in rows:
        rec = dict(zip(colnames, r))

        # Validação de NOT NULL críticos
        if any(rec.get(c) is None for c in REQUIRED_NOT_NULL):
            skipped += 1
            continue

        payload.append({c: rec.get(c) for c in TRUSTED_COLS})

    if not payload:
        print(f"[PARADAS] Nenhum registro válido para inserir/atualizar (skipped={skipped}).")
        return
    if skipped:
        print(f"[PARADAS] Registros pulados por campos NOT NULL ausentes: {skipped}")

    # 3) MERGE na TRUSTED (idempotente por IDPARADA)
    using_select = ",\n                ".join([f":{c} {c}" for c in TRUSTED_COLS])
    set_lines = ",\n            ".join([f"t.{c} = s.{c}" for c in TRUSTED_COLS if c != "IDPARADA"])

    merge_sql = f"""
        MERGE INTO {TARGET_TABLE} t
        USING (
            SELECT
                {using_select}
            FROM dual
        ) s
        ON (t.IDPARADA = s.IDPARADA)
        WHEN MATCHED THEN UPDATE SET
            {set_lines}
        WHEN NOT MATCHED THEN INSERT (
            {", ".join(TRUSTED_COLS)}
        ) VALUES (
            {", ".join("s."+c for c in TRUSTED_COLS)}
        )
    """

    trusted_conn = _make_oracle_conn(ORACLE_CONN_ID_TRUSTED)
    try:
        cur_t = trusted_conn.cursor()
        # executa em lotes
        for batch in _chunk(payload, size=1000):
            cur_t.executemany(merge_sql, batch)
        trusted_conn.commit()
    finally:
        trusted_conn.close()

with DAG(
    dag_id="etl_paradas_raw_to_trusted",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # se Airflow >= 2.4 pode usar schedule=None
    catchup=False,
    tags=["etl", "oracle", "paradas"],
):
    PythonOperator(
        task_id="merge_upsert_paradas",
        python_callable=etl_paradas_raw_to_trusted,
    )
