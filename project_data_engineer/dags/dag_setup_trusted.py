from datetime import datetime
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

ORACLE_CONN_ID = "oracle_trusted"

CREATE_TABLE_BLOCK = """
DECLARE
  v_exists NUMBER := 0;
BEGIN
  SELECT COUNT(*) INTO v_exists
    FROM USER_TABLES
   WHERE TABLE_NAME = '{{ params.table_name }}';

  IF v_exists = 0 THEN
    EXECUTE IMMEDIATE q'[
      {% include (params.table_name | lower) ~ '.sql' %}
    ]';
  END IF;
END;
"""

with DAG(
    dag_id="setup_schema_tables_trusted",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["oracle","setup","schema"],
    template_searchpath=["/home/adami/airflow/dags/sql/operacao_pp_trusted"], 
):
    def create_table_task(name: str):
        return SQLExecuteQueryOperator(
            task_id=f"create_tbl_{name.lower()}",
            conn_id=ORACLE_CONN_ID,
            sql=CREATE_TABLE_BLOCK,
            params={"table_name": name.upper()},
        )

    #t_clientes = create_table_task("CLIENTES")
    t_itens    = create_table_task("ITENS")
    #t_pedidos  = create_table_task("PEDIDOS")
    #t_facas    = create_table_task("FACAS")
    #t_maquina  = create_table_task("MAQUINA")
    #t_cliches  = create_table_task("CLICHES")
    #t_paradas  = create_table_task("PARADAS")
    #t_tarefcon = create_table_task("TAREFCON")
    #t_fi       = create_table_task("FI")

    [t_itens]
