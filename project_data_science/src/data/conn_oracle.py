import oracledb
import os
from dotenv import load_dotenv
import sys

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())




def load_env_oracle() -> oracledb.Connection:
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    host = os.getenv("ORACLE_HOST")
    port = os.getenv("ORACLE_PORT", "1521")
    service_name = os.getenv("ORACLE_SERVICE_NAME")
    
    print(f"User: {user}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Service: {service_name}")

    conn = oracledb.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        service_name=service_name
    )
    return conn
