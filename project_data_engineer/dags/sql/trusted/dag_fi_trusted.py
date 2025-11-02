from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Iterable

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
import oracledb

# --- Connection IDs (iguais ao da CLICHES) ---
ORACLE_CONN_ID_RAW = "oracle_raw"
ORACLE_CONN_ID_TRUSTED = "oracle_trusted"

# --- Tabela alvo ---
TARGET_TABLE = "FI"

# Colunas da TRUSTED (ordem do MERGE/INSERT)
TRUSTED_COLS = [
    "CODFI",
    "FIGURA",
    "DESATIVADOSN",
    "COR1",
    "COR2",
    "CONSUMOCOR2",
    "VISCOSIDADECOR2",
    "COR3",
    "CONSUMOCOR3",
    "COR4",
    "CONSUMOCOR4",
]

# Texto / numéricas na TRUSTED (p/ coerção + setinputsizes)
VARCHAR_COLS = {"CODFI", "FIGURA", "COR1", "COR2", "COR3", "COR4"}
NUMBER_COLS  = {"CONSUMOCOR2", "VISCOSIDADECOR2", "CONSUMOCOR3", "CONSUMOCOR4"}

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
    return str(v)[:1]  # garante exatamente 1 char

def etl_fi_raw_to_trusted(**context):
    # 1) Extrai da RAW apenas o layout da TRUSTED (mesmo padrão da CLICHES)
    select_sql = f"""
        SELECT
            CODFI,
            FIGURA,
            DESATIVADOSN,
            COR1,
            COR2,
            CONSUMOCOR2,
            VISCOSIDADECOR2,
            COR3,
            CONSUMOCOR3,
            COR4,
            CONSUMOCOR4
        FROM {TARGET_TABLE}
    """
    raw_conn = _make_oracle_conn(ORACLE_CONN_ID_RAW)
    try:
        cur = raw_conn.cursor()
        cur.execute(select_sql)
        colnames = [d[0] for d in cur.description]
        rows = cur.fetchall()
    finally:
        raw_conn.close()

    if not rows:
        return

    # 2) Transforma → coerção de tipos idêntica para todo o batch (evita DPY-3013)
    payload: List[Dict[str, Any]] = []
    for r in rows:
        rec = dict(zip(colnames, r))

        # Texto sempre str (evita int→VARCHAR)
        for c in VARCHAR_COLS:
            val = rec.get(c)
            rec[c] = None if val is None else str(val)

        # CHAR(1) normalizado
        rec["DESATIVADOSN"] = _char1(rec.get("DESATIVADOSN"))

        # NUMBER como float (aceita int/float/str numérica)
        for c in NUMBER_COLS:
            val = rec.get(c)
            if val is None:
                rec[c] = None
            else:
                rec[c] = float(val) if isinstance(val, (int, float)) else float(str(val))

        # Registro final no layout da TRUSTED
        payload.append({c: rec.get(c) for c in TRUSTED_COLS})

    # 3) MERGE idempotente por CODFI (mesmo padrão: USING DUAL + s.*)
    merge_sql = f"""
        MERGE INTO {TARGET_TABLE} t
        USING (
            SELECT
                :CODFI CODFI,
                :FIGURA FIGURA,
                :DESATIVADOSN DESATIVADOSN,
                :COR1 COR1,
                :COR2 COR2,
                :CONSUMOCOR2 CONSUMOCOR2,
                :VISCOSIDADECOR2 VISCOSIDADECOR2,
                :COR3 COR3,
                :CONSUMOCOR3 CONSUMOCOR3,
                :COR4 COR4,
                :CONSUMOCOR4 CONSUMOCOR4
            FROM dual
        ) s
        ON (t.CODFI = s.CODFI)
        WHEN MATCHED THEN UPDATE SET
            t.FIGURA           = s.FIGURA,
            t.DESATIVADOSN     = s.DESATIVADOSN,
            t.COR1             = s.COR1,
            t.COR2             = s.COR2,
            t.CONSUMOCOR2      = s.CONSUMOCOR2,
            t.VISCOSIDADECOR2  = s.VISCOSIDADECOR2,
            t.COR3             = s.COR3,
            t.CONSUMOCOR3      = s.CONSUMOCOR3,
            t.COR4             = s.COR4,
            t.CONSUMOCOR4      = s.CONSUMOCOR4
        WHEN NOT MATCHED THEN INSERT (
            {", ".join(TRUSTED_COLS)}
        ) VALUES (
            {", ".join("s."+c for c in TRUSTED_COLS)}
        )
    """

    trusted_conn = _make_oracle_conn(ORACLE_CONN_ID_TRUSTED)
    try:
        cur_t = trusted_conn.cursor()

        # (Opcional mas recomendável) travar os tipos de bind como na CLICHES
        cur_t.setinputsizes(
            CODFI=oracledb.DB_TYPE_VARCHAR,
            FIGURA=oracledb.DB_TYPE_VARCHAR,
            DESATIVADOSN=oracledb.DB_TYPE_CHAR,
            COR1=oracledb.DB_TYPE_VARCHAR,
            COR2=oracledb.DB_TYPE_VARCHAR,
            CONSUMOCOR2=oracledb.DB_TYPE_NUMBER,
            VISCOSIDADECOR2=oracledb.DB_TYPE_NUMBER,
            COR3=oracledb.DB_TYPE_VARCHAR,
            CONSUMOCOR3=oracledb.DB_TYPE_NUMBER,
            COR4=oracledb.DB_TYPE_VARCHAR,
            CONSUMOCOR4=oracledb.DB_TYPE_NUMBER,
        )

        for batch in _chunk(payload, size=1000):
            cur_t.executemany(merge_sql, batch)
        trusted_conn.commit()
    finally:
        trusted_conn.close()

with DAG(
    dag_id="etl_fi_raw_to_trusted",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # mesmo padrão
    catchup=False,
    tags=["etl", "oracle", "fi"],
):
    PythonOperator(
        task_id="merge_upsert_fi",
        python_callable=etl_fi_raw_to_trusted,
    )
