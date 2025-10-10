import oracledb
import os
from dotenv import load_dotenv, find_dotenv

# Carregar variáveis do .env
load_dotenv(find_dotenv())


def connect_oracle(user: str, password: str) -> oracledb.Connection:
    """Função genérica para criar a conexão Oracle"""
    host = os.getenv("ORACLE_HOST")
    port = os.getenv("ORACLE_PORT", "1521")
    service_name = os.getenv("ORACLE_SERVICE_NAME")

    print(f"User: {user}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Service: {service_name}")

    return oracledb.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        service_name=service_name
    )


def connect_oracle_raw() -> oracledb.Connection:
    """Conecta na camada RAW"""
    return connect_oracle(
        os.getenv("ORACLE_RAW_USER"),
        os.getenv("ORACLE_RAW_PASSWORD")
    )


def connect_oracle_trusted() -> oracledb.Connection:
    """Conecta na camada TRUSTED"""
    return connect_oracle(
        os.getenv("ORACLE_TRUSTED_USER"),
        os.getenv("ORACLE_TRUSTED_PASSWORD")
    )


def connect_oracle_refined() -> oracledb.Connection:
    """Conecta na camada REFINED"""
    return connect_oracle(
        os.getenv("ORACLE_REFINED_USER"),
        os.getenv("ORACLE_REFINED_PASSWORD")
    )
