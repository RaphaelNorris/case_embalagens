from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Iterable

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
import oracledb

# --- Connection IDs (ajuste se necessário) ---
ORACLE_CONN_ID_RAW = "oracle_raw"
ORACLE_CONN_ID_TRUSTED = "oracle_trusted"

# --- Tabela alvo (nome simples; se precisar, prefixe com o owner) ---
TARGET_TABLE = "CLIENTES"

# Colunas existentes na TRUSTED (conforme DDL informado com novos nomes)
TRUSTED_COLS = [
    "ID_CLIENTE",
    "TX_CLIENTE",
    "CD_CLIENTE",
    "CD_REPRESENTANTE",
    "TOLMAIS",
    "TOLMENOS",
    "RAZAOSOCIAL",
    "EXIGELAUDO",
    "IDUNICOREGISTRO",
    "ACEITAPALETEINCOMPLETO",
    "DESCACEITAPALETEINCOMPLETO",
    "DATACRIACAO",
    "DATAULTMODIF",
]

# Colunas da RAW (nomes originais)
RAW_COLS = [
    "IDCLIENTE",
    "CLIENTE",
    "CODCLIENTE",
    "CODREPRESENTANTE",
    "TOLMAIS",
    "TOLMENOS",
    "RAZAOSOCIAL",
    "EXIGELAUDO",
    "IDUNICOREGISTRO",
    "ACEITAPALETEINCOMPLETO",
    "DESCACEITAPALETEINCOMPLETO",
    "DATACRIACAO",
    "DATAULTMODIF",
]

# Mapeamento RAW → TRUSTED
COLUMN_MAPPING = {
    "IDCLIENTE": "ID_CLIENTE",
    "CLIENTE": "TX_CLIENTE",
    "CODCLIENTE": "CD_CLIENTE", 
    "CODREPRESENTANTE": "CD_REPRESENTANTE"
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


def _handle_nulls(value, col_type):
    """Trata valores NaN/NULL baseado no tipo da coluna"""
    if value is None:
        if "VARCHAR" in col_type:
            return ""
        elif "NUMBER" in col_type:
            return 0
        elif "CHAR" in col_type:
            return " "
        elif "DATE" in col_type or "TIMESTAMP" in col_type:
            return None  # Mantém NULL para datas
        else:
            return None
    return value


def etl_clientes_raw_to_trusted(**context):
    # 1) Extrai da RAW com nomes originais
    select_sql = f"""
        SELECT
            IDCLIENTE,
            CLIENTE,
            CODCLIENTE,
            CODREPRESENTANTE,
            TOLMAIS,
            TOLMENOS,
            RAZAOSOCIAL,
            EXIGELAUDO,
            IDUNICOREGISTRO,
            ACEITAPALETEINCOMPLETO,
            DESCACEITAPALETEINCOMPLETO,
            DATACRIACAO,
            DATAULTMODIF
        FROM {TARGET_TABLE}
    """

    raw_conn = _make_oracle_conn(ORACLE_CONN_ID_RAW)
    try:
        cur = raw_conn.cursor()
        cur.execute(select_sql)
        colnames = [d[0] for d in cur.description]  # nomes originais em UPPER
        rows = cur.fetchall()
    finally:
        raw_conn.close()

    if not rows:
        return

    # 2) Transforma → dicionários com mapeamento para TRUSTED + tratamento de NaNs
    payload: List[Dict[str, Any]] = []
    
    # Tipos das colunas na TRUSTED (simplificado para tratamento de NULLs)
    column_types = {
        "ID_CLIENTE": "NUMBER",
        "TX_CLIENTE": "VARCHAR2",
        "CD_CLIENTE": "VARCHAR2", 
        "CD_REPRESENTANTE": "VARCHAR",
        "TOLMAIS": "NUMBER",
        "TOLMENOS": "NUMBER",
        "RAZAOSOCIAL": "VARCHAR2",
        "EXIGELAUDO": "CHAR",
        "IDUNICOREGISTRO": "RAW",
        "ACEITAPALETEINCOMPLETO": "NUMBER",
        "DESCACEITAPALETEINCOMPLETO": "VARCHAR2",
        "DATACRIACAO": "TIMESTAMP",
        "DATAULTMODIF": "TIMESTAMP"
    }
    
    for r in rows:
        raw_rec = dict(zip(colnames, r))
        
        # Aplica mapeamento e tratamento de NULLs
        trusted_rec = {}
        for raw_col, trusted_col in COLUMN_MAPPING.items():
            value = raw_rec.get(raw_col)
            col_type = column_types.get(trusted_col, "VARCHAR2")
            trusted_rec[trusted_col] = _handle_nulls(value, col_type)
        
        # Adiciona colunas que não mudaram de nome
        for col in RAW_COLS:
            if col not in COLUMN_MAPPING:  # Colunas que mantêm o mesmo nome
                value = raw_rec.get(col)
                col_type = column_types.get(col, "VARCHAR2")
                trusted_rec[col] = _handle_nulls(value, col_type)
            
        payload.append(trusted_rec)

    # 3) MERGE idempotente na TRUSTED por ID_CLIENTE
    merge_sql = f"""
        MERGE INTO {TARGET_TABLE} t
        USING (
            SELECT
                :ID_CLIENTE ID_CLIENTE,
                :TX_CLIENTE TX_CLIENTE,
                :CD_CLIENTE CD_CLIENTE,
                :CD_REPRESENTANTE CD_REPRESENTANTE,
                :TOLMAIS TOLMAIS,
                :TOLMENOS TOLMENOS,
                :RAZAOSOCIAL RAZAOSOCIAL,
                :EXIGELAUDO EXIGELAUDO,
                :IDUNICOREGISTRO IDUNICOREGISTRO,
                :ACEITAPALETEINCOMPLETO ACEITAPALETEINCOMPLETO,
                :DESCACEITAPALETEINCOMPLETO DESCACEITAPALETEINCOMPLETO,
                :DATACRIACAO DATACRIACAO,
                :DATAULTMODIF DATAULTMODIF
            FROM dual
        ) s
        ON (t.ID_CLIENTE = s.ID_CLIENTE)
        WHEN MATCHED THEN UPDATE SET
            t.TX_CLIENTE                      = s.TX_CLIENTE,
            t.CD_CLIENTE                      = s.CD_CLIENTE,
            t.CD_REPRESENTANTE                = s.CD_REPRESENTANTE,
            t.TOLMAIS                         = s.TOLMAIS,
            t.TOLMENOS                        = s.TOLMENOS,
            t.RAZAOSOCIAL                     = s.RAZAOSOCIAL,
            t.EXIGELAUDO                      = s.EXIGELAUDO,
            t.IDUNICOREGISTRO                 = s.IDUNICOREGISTRO,
            t.ACEITAPALETEINCOMPLETO          = s.ACEITAPALETEINCOMPLETO,
            t.DESCACEITAPALETEINCOMPLETO      = s.DESCACEITAPALETEINCOMPLETO,
            t.DATACRIACAO                     = s.DATACRIACAO,
            t.DATAULTMODIF                    = s.DATAULTMODIF
        WHEN NOT MATCHED THEN INSERT (
            {", ".join(TRUSTED_COLS)}
        ) VALUES (
            {", ".join("s."+c for c in TRUSTED_COLS)}
        )
    """

    trusted_conn = _make_oracle_conn(ORACLE_CONN_ID_TRUSTED)
    try:
        cur_t = trusted_conn.cursor()
        for batch in _chunk(payload, size=1000):
            cur_t.executemany(merge_sql, batch)
        trusted_conn.commit()
    finally:
        trusted_conn.close()


with DAG(
    dag_id="etl_clientes_raw_to_trusted",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # se Airflow >= 2.4 pode usar schedule=None
    catchup=False,
    tags=["etl", "oracle", "clientes"],
):
    PythonOperator(
        task_id="merge_upsert_clientes",
        python_callable=etl_clientes_raw_to_trusted,
    )