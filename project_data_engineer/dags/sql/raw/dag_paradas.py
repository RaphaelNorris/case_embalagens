from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import oracledb

MSSQL_CONN_ID = "mssql_src"
ORACLE_CONN_ID = "oracle_raw"


def _make_mssql_engine():
    c = BaseHook.get_connection(MSSQL_CONN_ID)
    extra = c.extra_dejson or {}
    driver = extra.get("driver", "ODBC Driver 17 for SQL Server")
    trust = extra.get("TrustServerCertificate", "yes")
    odbc_connect = (
        f"DRIVER={{{driver}}};"
        f"SERVER={c.host},{c.port or 1433};"
        f"DATABASE={c.schema};"
        f"UID={c.login};PWD={c.password};"
        f"TrustServerCertificate={trust};"
    )
    url = URL.create("mssql+pyodbc", query={"odbc_connect": odbc_connect})
    return create_engine(url, fast_executemany=True)


def _make_oracle_conn():
    c = BaseHook.get_connection(ORACLE_CONN_ID)
    extra = c.extra_dejson or {}
    service_name = extra.get("service_name")
    sid = extra.get("sid")
    port = c.port or 1521
    if service_name:
        dsn = oracledb.makedsn(c.host, port, service_name=service_name)
    elif sid:
        dsn = oracledb.makedsn(c.host, port, sid=sid)
    else:
        dsn = oracledb.makedsn(c.host, port, service_name=c.schema)
    return oracledb.connect(user=c.login, password=c.password, dsn=dsn)


def _bit_to_char(v: Any) -> str:
    return "Y" if v in (1, True, "1", "Y", "y") else "N"


def _map_row_to_oracle(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "IDPARADA": row.get("idParada"),
        "PARADA": row.get("Parada"),
        "DESCRICAO": row.get("Descricao"),
        "SETOR": row.get("Setor"),
        "TIPO": row.get("Tipo"),
        "CODIGOERP": row.get("CodigoERP"),
        "MODOVALIDACAO": row.get("ModoValidacao"),
        "TEXTOVALIDACAO": row.get("TextoValidacao"),
        "USADAONDULADEIRA": _bit_to_char(row.get("UsadaOnduladeira")),
        "USADACONVERSAO": _bit_to_char(row.get("UsadaConversao")),
        "DESATIVADA": _bit_to_char(row.get("Desativada")),
        "FLAGAJUSTE": _bit_to_char(row.get("flagAjuste")),
        "FLAGEXTERNA": _bit_to_char(row.get("flagExterna")),
        "FLAGCONTINUACAOAJUSTE": _bit_to_char(row.get("FlagContinuacaoAjuste")),
        "FLAGASSOCIADOAOPRODUTO": _bit_to_char(row.get("FlagAssociadoAoProduto")),
        "FORCATROCACONVERSAOONLINE": _bit_to_char(row.get("ForcaTrocaConversaoOnline")),
        "EXCLUIOEE": _bit_to_char(row.get("ExcluiOEE")),
        "EXIGEINFORMACAOSECAOMAQCONV": _bit_to_char(row.get("ExigeInformacaoSecaoMaqConv")),
    }


def etl_paradas(**context):
    mssql = _make_mssql_engine()
    sql = text("""
        SELECT
            idParada,
            Parada,
            Descricao,
            Setor,
            Tipo,
            CodigoERP,
            ModoValidacao,
            TextoValidacao,
            UsadaOnduladeira,
            UsadaConversao,
            Desativada,
            flagAjuste,
            flagExterna,
            FlagContinuacaoAjuste,
            FlagAssociadoAoProduto,
            ForcaTrocaConversaoOnline,
            ExcluiOEE,
            ExigeInformacaoSecaoMaqConv
        FROM PARADAS
    """)
    with mssql.connect() as conn:
        rows = [dict(r) for r in conn.execute(sql).mappings().all()]
    if not rows:
        return
    payload: List[Dict[str, Any]] = [_map_row_to_oracle(r) for r in rows]

    merge_sql = """
        MERGE INTO PARADAS tgt
        USING (
            SELECT
                :IDPARADA AS IDPARADA,
                :PARADA AS PARADA,
                :DESCRICAO AS DESCRICAO,
                :SETOR AS SETOR,
                :TIPO AS TIPO,
                :CODIGOERP AS CODIGOERP,
                :MODOVALIDACAO AS MODOVALIDACAO,
                :TEXTOVALIDACAO AS TEXTOVALIDACAO,
                :USADAONDULADEIRA AS USADAONDULADEIRA,
                :USADACONVERSAO AS USADACONVERSAO,
                :DESATIVADA AS DESATIVADA,
                :FLAGAJUSTE AS FLAGAJUSTE,
                :FLAGEXTERNA AS FLAGEXTERNA,
                :FLAGCONTINUACAOAJUSTE AS FLAGCONTINUACAOAJUSTE,
                :FLAGASSOCIADOAOPRODUTO AS FLAGASSOCIADOAOPRODUTO,
                :FORCATROCACONVERSAOONLINE AS FORCATROCACONVERSAOONLINE,
                :EXCLUIOEE AS EXCLUIOEE,
                :EXIGEINFORMACAOSECAOMAQCONV AS EXIGEINFORMACAOSECAOMAQCONV
            FROM dual
        ) src
        ON (tgt.IDPARADA = src.IDPARADA)
        WHEN MATCHED THEN UPDATE SET
            tgt.PARADA = src.PARADA,
            tgt.DESCRICAO = src.DESCRICAO,
            tgt.SETOR = src.SETOR,
            tgt.TIPO = src.TIPO,
            tgt.CODIGOERP = src.CODIGOERP,
            tgt.MODOVALIDACAO = src.MODOVALIDACAO,
            tgt.TEXTOVALIDACAO = src.TEXTOVALIDACAO,
            tgt.USADAONDULADEIRA = src.USADAONDULADEIRA,
            tgt.USADACONVERSAO = src.USADACONVERSAO,
            tgt.DESATIVADA = src.DESATIVADA,
            tgt.FLAGAJUSTE = src.FLAGAJUSTE,
            tgt.FLAGEXTERNA = src.FLAGEXTERNA,
            tgt.FLAGCONTINUACAOAJUSTE = src.FLAGCONTINUACAOAJUSTE,
            tgt.FLAGASSOCIADOAOPRODUTO = src.FLAGASSOCIADOAOPRODUTO,
            tgt.FORCATROCACONVERSAOONLINE = src.FORCATROCACONVERSAOONLINE,
            tgt.EXCLUIOEE = src.EXCLUIOEE,
            tgt.EXIGEINFORMACAOSECAOMAQCONV = src.EXIGEINFORMACAOSECAOMAQCONV
        WHEN NOT MATCHED THEN INSERT (
            IDPARADA, PARADA, DESCRICAO, SETOR, TIPO, CODIGOERP, MODOVALIDACAO, TEXTOVALIDACAO,
            USADAONDULADEIRA, USADACONVERSAO, DESATIVADA, FLAGAJUSTE, FLAGEXTERNA,
            FLAGCONTINUACAOAJUSTE, FLAGASSOCIADOAOPRODUTO, FORCATROCACONVERSAOONLINE,
            EXCLUIOEE, EXIGEINFORMACAOSECAOMAQCONV
        ) VALUES (
            src.IDPARADA, src.PARADA, src.DESCRICAO, src.SETOR, src.TIPO, src.CODIGOERP, src.MODOVALIDACAO, src.TEXTOVALIDACAO,
            src.USADAONDULADEIRA, src.USADACONVERSAO, src.DESATIVADA, src.FLAGAJUSTE, src.FLAGEXTERNA,
            src.FLAGCONTINUACAOAJUSTE, src.FLAGASSOCIADOAOPRODUTO, src.FORCATROCACONVERSAOONLINE,
            src.EXCLUIOEE, src.EXIGEINFORMACAOSECAOMAQCONV
        )
    """

    conn = _make_oracle_conn()
    try:
        cur = conn.cursor()
        cur.executemany(merge_sql, payload)
        conn.commit()
    finally:
        conn.close()


with DAG(
    dag_id="etl_paradas",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "sqlserver", "oracle", "paradas"],
):
    merge_upsert_paradas = PythonOperator(
        task_id="merge_upsert_paradas",
        python_callable=etl_paradas,
    )
