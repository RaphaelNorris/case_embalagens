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
        "CODFI": row.get("CodFI"),
        "LOCALIZACAO": row.get("Localizacao"),
        "FIGURA": row.get("Figura"),
        "STATUS": row.get("Status"),
        "FACESIMPRESSAS": row.get("FacesImpressas"),
        "ABASIMPRESSAS": row.get("AbasImpressas"),
        "OBS": row.get("Obs"),
        "DESCRSTATUSFI": row.get("DescrStatusFI"),
        "DESATIVADOSN": _bit_to_char(row.get("DesativadoSN")),
        "COR1": row.get("Cor1"),
        "CONSUMOCOR1": row.get("ConsumoCor1"),
        "VISCOSIDADECOR1": row.get("ViscosidadeCor1"),
        "COR2": row.get("Cor2"),
        "CONSUMOCOR2": row.get("ConsumoCor2"),
        "VISCOSIDADECOR2": row.get("ViscosidadeCor2"),
        "COR3": row.get("Cor3"),
        "CONSUMOCOR3": row.get("ConsumoCor3"),
        "VISCOSIDADECOR3": row.get("ViscosidadeCor3"),
        "COR4": row.get("Cor4"),
        "CONSUMOCOR4": row.get("ConsumoCor4"),
        "VISCOSIDADECOR4": row.get("ViscosidadeCor4"),
        "COR5": row.get("Cor5"),
        "CONSUMOCOR5": row.get("ConsumoCor5"),
        "VISCOSIDADECOR5": row.get("ViscosidadeCor5"),
        "COR6": row.get("Cor6"),
        "CONSUMOCOR6": row.get("ConsumoCor6"),
        "VISCOSIDADECOR6": row.get("ViscosidadeCor6"),
    }


def etl_fi(**context):
    src = _make_mssql_engine()
    sql = text("""
        SELECT
            CodFI,
            Localizacao,
            Figura,
            Status,
            FacesImpressas,
            AbasImpressas,
            Obs,
            DescrStatusFI,
            DesativadoSN,
            Cor1, ConsumoCor1, ViscosidadeCor1,
            Cor2, ConsumoCor2, ViscosidadeCor2,
            Cor3, ConsumoCor3, ViscosidadeCor3,
            Cor4, ConsumoCor4, ViscosidadeCor4,
            Cor5, ConsumoCor5, ViscosidadeCor5,
            Cor6, ConsumoCor6, ViscosidadeCor6
        FROM FI
    """)
    with src.connect() as conn:
        rows = [dict(r) for r in conn.execute(sql).mappings().all()]
    if not rows:
        return
    payload: List[Dict[str, Any]] = [_map_row_to_oracle(r) for r in rows]

    merge_sql = """
        MERGE INTO FI T
        USING (
            SELECT
                :CODFI CODFI,
                :LOCALIZACAO LOCALIZACAO,
                :FIGURA FIGURA,
                :STATUS STATUS,
                :FACESIMPRESSAS FACESIMPRESSAS,
                :ABASIMPRESSAS ABASIMPRESSAS,
                :OBS OBS,
                :DESCRSTATUSFI DESCRSTATUSFI,
                :DESATIVADOSN DESATIVADOSN,
                :COR1 COR1,
                :CONSUMOCOR1 CONSUMOCOR1,
                :VISCOSIDADECOR1 VISCOSIDADECOR1,
                :COR2 COR2,
                :CONSUMOCOR2 CONSUMOCOR2,
                :VISCOSIDADECOR2 VISCOSIDADECOR2,
                :COR3 COR3,
                :CONSUMOCOR3 CONSUMOCOR3,
                :VISCOSIDADECOR3 VISCOSIDADECOR3,
                :COR4 COR4,
                :CONSUMOCOR4 CONSUMOCOR4,
                :VISCOSIDADECOR4 VISCOSIDADECOR4,
                :COR5 COR5,
                :CONSUMOCOR5 CONSUMOCOR5,
                :VISCOSIDADECOR5 VISCOSIDADECOR5,
                :COR6 COR6,
                :CONSUMOCOR6 CONSUMOCOR6,
                :VISCOSIDADECOR6 VISCOSIDADECOR6
            FROM dual
        ) S
        ON (T.CODFI = S.CODFI)
        WHEN MATCHED THEN UPDATE SET
            T.LOCALIZACAO = S.LOCALIZACAO,
            T.FIGURA = S.FIGURA,
            T.STATUS = S.STATUS,
            T.FACESIMPRESSAS = S.FACESIMPRESSAS,
            T.ABASIMPRESSAS = S.ABASIMPRESSAS,
            T.OBS = S.OBS,
            T.DESCRSTATUSFI = S.DESCRSTATUSFI,
            T.DESATIVADOSN = S.DESATIVADOSN,
            T.COR1 = S.COR1,
            T.CONSUMOCOR1 = S.CONSUMOCOR1,
            T.VISCOSIDADECOR1 = S.VISCOSIDADECOR1,
            T.COR2 = S.COR2,
            T.CONSUMOCOR2 = S.CONSUMOCOR2,
            T.VISCOSIDADECOR2 = S.VISCOSIDADECOR2,
            T.COR3 = S.COR3,
            T.CONSUMOCOR3 = S.CONSUMOCOR3,
            T.VISCOSIDADECOR3 = S.VISCOSIDADECOR3,
            T.COR4 = S.COR4,
            T.CONSUMOCOR4 = S.CONSUMOCOR4,
            T.VISCOSIDADECOR4 = S.VISCOSIDADECOR4,
            T.COR5 = S.COR5,
            T.CONSUMOCOR5 = S.CONSUMOCOR5,
            T.VISCOSIDADECOR5 = S.VISCOSIDADECOR5,
            T.COR6 = S.COR6,
            T.CONSUMOCOR6 = S.CONSUMOCOR6,
            T.VISCOSIDADECOR6 = S.VISCOSIDADECOR6
        WHEN NOT MATCHED THEN INSERT (
            CODFI, LOCALIZACAO, FIGURA, STATUS, FACESIMPRESSAS, ABASIMPRESSAS, OBS,
            DESCRSTATUSFI, DESATIVADOSN, COR1, CONSUMOCOR1, VISCOSIDADECOR1,
            COR2, CONSUMOCOR2, VISCOSIDADECOR2,
            COR3, CONSUMOCOR3, VISCOSIDADECOR3,
            COR4, CONSUMOCOR4, VISCOSIDADECOR4,
            COR5, CONSUMOCOR5, VISCOSIDADECOR5,
            COR6, CONSUMOCOR6, VISCOSIDADECOR6
        ) VALUES (
            S.CODFI, S.LOCALIZACAO, S.FIGURA, S.STATUS, S.FACESIMPRESSAS, S.ABASIMPRESSAS, S.OBS,
            S.DESCRSTATUSFI, S.DESATIVADOSN, S.COR1, S.CONSUMOCOR1, S.VISCOSIDADECOR1,
            S.COR2, S.CONSUMOCOR2, S.VISCOSIDADECOR2,
            S.COR3, S.CONSUMOCOR3, S.VISCOSIDADECOR3,
            S.COR4, S.CONSUMOCOR4, S.VISCOSIDADECOR4,
            S.COR5, S.CONSUMOCOR5, S.VISCOSIDADECOR5,
            S.COR6, S.CONSUMOCOR6, S.VISCOSIDADECOR6
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
    dag_id="etl_fi",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "sqlserver", "oracle", "fi"],
):
    merge_upsert = PythonOperator(
        task_id="merge_upsert_fi",
        python_callable=etl_fi,
    )
