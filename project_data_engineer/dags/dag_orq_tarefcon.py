from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'orchestrator_etl_tarefcon',
    default_args=default_args,
    description='DAG para orquestrar o pipeline ETL completo',
    schedule_interval='25 17 * * *',  # Executa diariamente às 10:30
    catchup=False,
    tags=['orchestration', 'etl', 'tarefcon'],
) as dag:

    # Trigger da primeira DAG (MySQL para RAW)
    trigger_etl_tarefcon = TriggerDagRunOperator(
        task_id='trigger_etl_tarefcon',
        trigger_dag_id='etl_tarefcon',
        wait_for_completion=True,  # Aguarda a conclusão antes de prosseguir
        execution_date='{{ execution_date }}',
        reset_dag_run=True,
        poke_interval=30,  # Verifica a cada 30 segundos se a DAG terminou
    )

    # Trigger da segunda DAG (RAW para TRUSTED)
    trigger_raw_to_trusted = TriggerDagRunOperator(
        task_id='trigger_raw_to_trusted_tarefcon',
        trigger_dag_id='etl_raw_to_trusted_tarefcon',
        wait_for_completion=True,
        execution_date='{{ execution_date }}',
        reset_dag_run=True,
        poke_interval=30,
    )

    # Trigger da terceira DAG (TRUSTED para REFINED)
    trigger_trusted_to_refined = TriggerDagRunOperator(
        task_id='trigger_trusted_to_refined_tarefcon',
        trigger_dag_id='etl_trusted_to_refined_tarefcon',
        wait_for_completion=True,
        execution_date='{{ execution_date }}',
        reset_dag_run=True,
        poke_interval=30,
    )

    # Define a ordem de execução
    trigger_etl_tarefcon >> trigger_raw_to_trusted >> trigger_trusted_to_refined

    # Documentação das tarefas
    trigger_etl_tarefcon.doc_md = """
    ### Trigger DAG 1 - etl_tarefcon
    Dispara a execução da DAG que carrega dados do MySQL para a camada RAW no Oracle.
    Aguarda a conclusão completa antes de prosseguir para a próxima etapa.
    """

    trigger_raw_to_trusted.doc_md = """
    ### Trigger DAG 2 - etl_raw_to_trusted_tarefcon
    Dispara a execução da DAG que transforma dados da camada RAW para TRUSTED no Oracle.
    Só executa após a conclusão bem-sucedida da DAG anterior.
    """

    trigger_trusted_to_refined.doc_md = """
    ### Trigger DAG 3 - etl_trusted_to_refined_tarefcon
    Dispara a execução da DAG que transforma dados da camada TRUSTED para REFINED no Oracle.
    Etapa final do pipeline ETL.
    """