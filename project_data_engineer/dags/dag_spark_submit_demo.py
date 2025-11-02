from datetime import datetime
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

with DAG(
    dag_id="dag_spark_submit_demo",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["spark", "teste"],
) as dag:
    wordcount = SparkSubmitOperator(
        task_id="wordcount",
        application="/home/adami/airflow/jobs/pyspark_demo.py",
        conn_id="spark_local",
        spark_binary="/opt/spark/bin/spark-submit",
        name="wordcount-demo",
        verbose=True,
        env_vars={
            "PYSPARK_PYTHON": "/home/adami/airflow_venv/bin/python",
            "JAVA_HOME": "/usr/lib/jvm/java-17-openjdk-amd64",
            "SPARK_HOME": "/opt/spark",
        },
        conf={"spark.master": "local[*]"},  # reforço extra
    )
