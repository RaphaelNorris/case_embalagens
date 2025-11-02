from __future__ import annotations
from datetime import datetime
from typing import Any

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
import oracledb

ORACLE_CONN_ID_TRUSTED = "oracle_trusted"

TABLES_TO_DROP = ["ITENS"]

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

def drop_single_table(table_name: str, **context: Any):
    """
    Dropa uma tabela na schema conectada, ignorando ORA-00942 (tabela não existe).
    Usa CASCADE CONSTRAINTS e PURGE para remover dependências e não enviar à RECYCLEBIN.
    """
    sql = f"BEGIN EXECUTE IMMEDIATE 'DROP TABLE {table_name} CASCADE CONSTRAINTS PURGE'; END;"
    conn = _make_oracle_conn(ORACLE_CONN_ID_TRUSTED)
    try:
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            print(f"[DROP] Tabela {table_name}: drop efetuado com sucesso.")
        except oracledb.Error as e:
            if hasattr(e, "args") and e.args and len(e.args) > 0:
                err = e.args[0]
                code = getattr(err, "code", None)
                if code == 942:
                    print(f"[DROP] Tabela {table_name}: não existe (ORA-00942). Ignorando.")
                else:
                    raise
            else:
                raise
    finally:
        conn.close()

with DAG(
    dag_id="drop_trusted_tables",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["maintenance", "oracle", "drop", "trusted"],
) as dag:

    drop_tasks = []
    for tname in TABLES_TO_DROP:
        task = PythonOperator(
            task_id=f"drop_{tname.lower()}",
            python_callable=drop_single_table,
            op_kwargs={"table_name": tname},
        )
        drop_tasks.append(task)
