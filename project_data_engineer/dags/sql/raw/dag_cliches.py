from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List
import binascii
import pyodbc
import oracledb

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
from airflow.utils.log.logging_mixin import LoggingMixin

# -----------------
# Conexões (Airflow)
# -----------------
MSSQL_CONN_ID = "mssql_src"     # origem: SQL Server
ORACLE_CONN_ID = "oracle_raw"   # destino: Oracle

log = LoggingMixin().log

# -----------------
# Helpers/conexões
# -----------------
def _make_mssql_conn():
    """
    Conecta no SQL Server via pyodbc usando a Connection do Airflow (mssql_src).
    """
    c = BaseHook.get_connection(MSSQL_CONN_ID)
    
    # Construir connection string para SQL Server
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={c.host},{c.port or 1433};"
        f"DATABASE={c.schema or ''};"
        f"UID={c.login};"
        f"PWD={c.password};"
        "Encrypt=no;"
    )
    
    conn = pyodbc.connect(conn_str)
    return conn

def _make_oracle_conn():
    """
    Conecta no Oracle via oracledb usando a Connection do Airflow (oracle_raw).
    """
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

# -----------------
# Converters/mapeamentos para CLICHES
# -----------------
def _bit_to_char(v: Any) -> str:
    if v is None:
        return "N"
    return "Y" if v in (1, True, "1", "Y", "y") else "N"

def _convert_to_timestamp(value):
    """
    Converte para TIMESTAMP do Oracle mantendo hora, minuto, segundo e microssegundos.
    """
    if value is None:
        return None
    
    # Se já for datetime, retorna como está (o oracledb converte automaticamente)
    if isinstance(value, datetime):
        return value
    
    # Se for string, tenta converter para datetime
    if isinstance(value, str):
        try:
            # Tenta converter formatos comuns do SQL Server
            for fmt in [
                '%Y-%m-%d %H:%M:%S.%f', 
                '%Y-%m-%d %H:%M:%S', 
                '%d/%m/%Y %H:%M:%S',
                '%d/%m/%y %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f'
            ]:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            # Se nenhum formato funcionar, tenta parser genérico
            from dateutil import parser
            return parser.parse(value)
        except Exception as e:
            log.warning("Não foi possível converter data '%s': %s", value, str(e))
            return None
    
    # Se for outro tipo (date, etc), converte para datetime
    try:
        return datetime.combine(value, datetime.min.time())
    except Exception:
        return None

def _map_row_to_oracle_cliches(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeamento das colunas do SQL Server para Oracle para a tabela CLICHES.
    """
    return {
        "CODCLICHE": row.get("CodCliche"),
        "TIPO": row.get("Tipo"),
        "DESCRTIPOCLICHE": row.get("DescrTipoCliche"),
        "FORNECEDOR": row.get("Fornecedor"),
        "MODULO": row.get("Modulo"),
        "ARQUIVO": row.get("Arquivo"),
        "LOCALIZACAO": row.get("Localizacao"),
        "FIGURA": row.get("Figura"),
        "STATUS": row.get("Status"),
        "PRECO": row.get("Preco"),
        "AREA": row.get("Area"),
        "IDCLIENTE": row.get("IDCliente"),
        "OBS": row.get("Obs"),
        "CODIGOERP": row.get("CodigoERP"),
        "CHAVEESTADOFERRAMENTA": row.get("ChaveEstadoFerramenta"),
        "DESATIVADOSN": _bit_to_char(row.get("DesativadoSN")),
        "DATACRIACAOREGISTRO": _convert_to_timestamp(row.get("DataCriacaoRegistro")),
    }

# -----------------
# Tarefa principal para CLICHES
# -----------------
def etl_cliches(**context):
    # 1) Extrai do SQL Server
    sql = "SELECT * FROM CLICHES"
    src_conn = _make_mssql_conn()
    try:
        with src_conn.cursor() as cur:
            cur.execute(sql)
            columns = [column[0] for column in cur.description]
            rows = []
            for row in cur.fetchall():
                rows.append(dict(zip(columns, row)))
        log.info("SQL Server -> %s registros extraídos da tabela CLICHES.", len(rows))
        
        # Log para debug - verificar como as datas estão vindo
        if rows:
            sample_row = rows[0]
            log.info("Exemplo de DataCriacaoRegistro na origem: %s (tipo: %s)", 
                    sample_row.get("DataCriacaoRegistro"), 
                    type(sample_row.get("DataCriacaoRegistro")))
            
    except Exception as e:
        log.error("Erro ao extrair dados do SQL Server: %s", str(e))
        raise
    finally:
        src_conn.close()

    if not rows:
        log.info("Nenhum dado de origem. Nada a fazer.")
        return

    # 2) Mapeia para o layout do Oracle
    payload: List[Dict[str, Any]] = []
    for r in rows:
        try:
            mapped_row = _map_row_to_oracle_cliches(r)
            
            # Log para debug - verificar como as datas ficaram após mapeamento
            if not payload:  # Apenas no primeiro registro
                log.info("Exemplo de DATACRIACAOREGISTRO após mapeamento: %s (tipo: %s)", 
                        mapped_row.get("DATACRIACAOREGISTRO"), 
                        type(mapped_row.get("DATACRIACAOREGISTRO")))
            
            payload.append(mapped_row)
        except Exception as e:
            log.warning("Erro ao mapear linha: %s. Linha ignorada.", str(e))
            continue

    if not payload:
        log.info("Nenhum dado válido para processar após mapeamento.")
        return

    # 3) MERGE no Oracle
    merge_sql = """
        MERGE INTO CLICHES T
        USING (
            SELECT
                :CODCLICHE CODCLICHE,
                :TIPO TIPO,
                :DESCRTIPOCLICHE DESCRTIPOCLICHE,
                :FORNECEDOR FORNECEDOR,
                :MODULO MODULO,
                :ARQUIVO ARQUIVO,
                :LOCALIZACAO LOCALIZACAO,
                :FIGURA FIGURA,
                :STATUS STATUS,
                :PRECO PRECO,
                :AREA AREA,
                :IDCLIENTE IDCLIENTE,
                :OBS OBS,
                :CODIGOERP CODIGOERP,
                :CHAVEESTADOFERRAMENTA CHAVEESTADOFERRAMENTA,
                :DESATIVADOSN DESATIVADOSN,
                :DATACRIACAOREGISTRO DATACRIACAOREGISTRO
            FROM dual
        ) S
        ON (T.CODCLICHE = S.CODCLICHE)
        WHEN MATCHED THEN UPDATE SET
            T.TIPO = S.TIPO,
            T.DESCRTIPOCLICHE = S.DESCRTIPOCLICHE,
            T.FORNECEDOR = S.FORNECEDOR,
            T.MODULO = S.MODULO,
            T.ARQUIVO = S.ARQUIVO,
            T.LOCALIZACAO = S.LOCALIZACAO,
            T.FIGURA = S.FIGURA,
            T.STATUS = S.STATUS,
            T.PRECO = S.PRECO,
            T.AREA = S.AREA,
            T.IDCLIENTE = S.IDCLIENTE,
            T.OBS = S.OBS,
            T.CODIGOERP = S.CODIGOERP,
            T.CHAVEESTADOFERRAMENTA = S.CHAVEESTADOFERRAMENTA,
            T.DESATIVADOSN = S.DESATIVADOSN,
            T.DATACRIACAOREGISTRO = S.DATACRIACAOREGISTRO
        WHEN NOT MATCHED THEN INSERT (
            CODCLICHE, TIPO, DESCRTIPOCLICHE, FORNECEDOR, MODULO, ARQUIVO,
            LOCALIZACAO, FIGURA, STATUS, PRECO, AREA, IDCLIENTE, OBS,
            CODIGOERP, CHAVEESTADOFERRAMENTA, DESATIVADOSN, DATACRIACAOREGISTRO
        ) VALUES (
            S.CODCLICHE, S.TIPO, S.DESCRTIPOCLICHE, S.FORNECEDOR, S.MODULO, S.ARQUIVO,
            S.LOCALIZACAO, S.FIGURA, S.STATUS, S.PRECO, S.AREA, S.IDCLIENTE, S.OBS,
            S.CODIGOERP, S.CHAVEESTADOFERRAMENTA, S.DESATIVADOSN, S.DATACRIACAOREGISTRO
        )
    """

    dst = _make_oracle_conn()
    try:
        cur = dst.cursor()
        
        # Configurar inputs específicos para TIMESTAMP
        for param in payload:
            if 'DATACRIACAOREGISTRO' in param and isinstance(param['DATACRIACAOREGISTRO'], datetime):
                # Garantir que temos microssegundos para TIMESTAMP
                if param['DATACRIACAOREGISTRO'].microsecond == 0:
                    # Se não tem microssegundos, adiciona alguns para preencher
                    param['DATACRIACAOREGISTRO'] = param['DATACRIACAOREGISTRO'].replace(microsecond=123456)
        
        cur.executemany(merge_sql, payload)
        dst.commit()
        log.info("Oracle <- %s registros mergeados com sucesso na tabela CLICHES.", len(payload))
        
        # Log final para verificação
        if payload:
            sample = payload[0]
            log.info("DATACRIACAOREGISTRO enviada para Oracle: %s", sample.get("DATACRIACAOREGISTRO"))
            
    except Exception as e:
        log.error("Erro ao fazer MERGE no Oracle: %s", str(e))
        dst.rollback()
        raise
    finally:
        dst.close()

# -----------------
# DAG para CLICHES
# -----------------
with DAG(
    dag_id="etl_cliches",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "sqlserver", "oracle", "cliches"],
    default_args={
        'retries': 2,
    }
):
    load_task = PythonOperator(
        task_id="merge_upsert_cliches",
        python_callable=etl_cliches,
    )