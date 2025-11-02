from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="zz_hello",
    start_date=datetime(2025,1,1),
    schedule=None,
    catchup=False,
    tags=["debug"],
    description="DAG mínima para verificar descoberta",
):
    EmptyOperator(task_id="ok")

