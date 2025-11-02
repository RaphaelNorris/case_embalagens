from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_teste_vscode",
    description="DAG de teste criada no VS Code (VM)",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # execução manual
    catchup=False,
    tags=["teste"],
) as dag:
    hello = BashOperator(
        task_id="hello",
        bash_command="echo 'Airflow OK a partir da VM!'"
    )