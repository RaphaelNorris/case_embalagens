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
ORACLE_CONN_ID_TRUSTED = "oracle_trusted"  # origem: TRUSTED
ORACLE_CONN_ID_REFINED = "oracle_refined"  # destino: REFINED

log = LoggingMixin().log

# -----------------
# Helpers/conexões
# -----------------
def _make_oracle_conn_trusted():
    """
    Conecta no Oracle via oracledb usando a Connection do Airflow (oracle_trusted).
    """
    c = BaseHook.get_connection(ORACLE_CONN_ID_TRUSTED)
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

def _make_oracle_conn_refined():
    """
    Conecta no Oracle via oracledb usando a Connection do Airflow (oracle_refined).
    """
    c = BaseHook.get_connection(ORACLE_CONN_ID_REFINED)
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
# Converters/mapeamentos
# -----------------
def _handle_nan(value, nan_value):
    """
    Trata valores NaN/NULL conforme especificado.
    """
    if value is None:
        return nan_value
    
    # Para strings vazias
    if isinstance(value, str) and value.strip() == "":
        return nan_value
    
    # Para números
    if isinstance(value, (int, float)) and (value == 0 or value == -1):
        return value  # Mantém o valor se já for o padrão
    
    try:
        # Verifica se é NaN numérico
        if isinstance(value, float) and value != value:  # NaN check
            return nan_value
    except:
        pass
    
    return value

def _convert_to_varchar(value, nan_value, field_name=None):
    """
    Converte para VARCHAR com tratamento de NaN.
    Campos TX_ SEMPRE retornam string, nunca NULL.
    """
    # Se for campo TX_, força retorno de string vazia para NULL
    if field_name and field_name.startswith('TX_'):
        if value is None:
            return " "
        if isinstance(value, str):
            return value if value.strip() != "" else ""
        else:
            try:
                str_value = str(value)
                return str_value if str_value.strip() != "" else ""
            except:
                return ""
    
    # Para outros campos, mantém a lógica original
    else:
        if value is None:
            return nan_value
        if isinstance(value, str):
            return value if value.strip() != "" else nan_value
        else:
            try:
                str_value = str(value)
                return str_value if str_value.strip() != "" else nan_value
            except:
                return nan_value

def _convert_to_number(value, nan_value):
    """
    Converte para NUMBER com tratamento de NaN.
    """
    if value is None:
        return nan_value
    
    try:
        if isinstance(value, (int, float)):
            # Verifica se é NaN
            if isinstance(value, float) and value != value:
                return nan_value
            return value
        
        # Converte string para número
        str_value = str(value).strip()
        if str_value == "":
            return nan_value
        
        # Tenta converter para int ou float
        if '.' in str_value:
            return float(str_value)
        else:
            return int(str_value)
            
    except (ValueError, TypeError):
        return nan_value

def _map_row_to_refined_maquina(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeamento da TRUSTED para REFINED com conversões de tipo e tratamento de NaN.
    """
    # DEBUG: Log para verificar a estrutura dos dados
    if not hasattr(_map_row_to_refined_maquina, 'logged_structure'):
        log.info("Estrutura da linha recebida da TRUSTED: %s", list(row.keys())[:10])
        _map_row_to_refined_maquina.logged_structure = True
    
    return {
        "TX_MAQUINA": _convert_to_varchar(row.get("TX_MAQUINA") or row.get("MAQUINA"), " ", "TX_MAQUINA"),
        "TX_TIPO": _convert_to_varchar(row.get("TX_TIPO") or row.get("TIPO"), " ", "TX_TIPO"),
        "QT_NRDECORES": _convert_to_number(row.get("QT_NRDECORES") or row.get("NRDECORES"), 0),
        "ID_GRUPOMAQUINA": _convert_to_varchar(row.get("IDGRUPOMAQUINA"), "-1", "ID_GRUPOMAQUINA"),
    }

# -----------------
# Tarefa principal
# -----------------
def etl_maquina_trusted_to_refined(**context):
    total_processed = 0
    
    # 1) TRUNCATE na tabela de destino REFINED
    log.info("REFINED -> Executando TRUNCATE na tabela MAQUINA...")
    dst_conn = _make_oracle_conn_refined()
    try:
        with dst_conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE MAQUINA")
        dst_conn.commit()
        log.info("REFINED -> TRUNCATE executado com sucesso na tabela MAQUINA.")
    except Exception as e:
        log.error("Erro ao executar TRUNCATE no Oracle REFINED: %s", str(e))
        dst_conn.rollback()
        raise
    finally:
        dst_conn.close()

    # Extração e processamento SEM PAGINAÇÃO
    sql = "SELECT * FROM MAQUINA"
    
    src_conn = _make_oracle_conn_trusted()
    try:
        with src_conn.cursor() as cur:
            cur.execute(sql)
            columns = [column[0] for column in cur.description]
            rows = []
            for row in cur.fetchall():
                rows.append(dict(zip(columns, row)))
        
        log.info("TRUSTED -> %s registros extraídos da tabela MAQUINA.", len(rows))

        if not rows:
            log.info("Nenhum registro para processar.")
            return

        # 2) Mapeia para o layout do REFINED
        payload = []
        mapping_errors = 0
        
        for r in rows:
            try:
                mapped_row = _map_row_to_refined_maquina(r)
                # Verifica se o mapeamento não está vazio
                if any(value is not None for value in mapped_row.values()):
                    payload.append(mapped_row)
                else:
                    mapping_errors += 1
            except Exception as e:
                log.warning("Erro ao mapear linha: %s. Linha ignorada.", str(e))
                mapping_errors += 1
                continue

        if mapping_errors > 0:
            log.warning("%s registros com erro de mapeamento", mapping_errors)

        if payload:
            # DEBUG: Mostrar primeiro registro mapeado
            log.info("Primeiro registro mapeado para REFINED: %s", {k: v for k, v in list(payload[0].items())[:3]})
            
            # 3) Processa todos os registros de uma vez
            _process_batch_maquina_refined(payload)
            total_processed = len(payload)
            log.info("Processamento concluído: %s registros válidos inseridos.", total_processed)
        else:
            log.info("Nenhum registro válido para processar.")

    except Exception as e:
        log.error("Erro ao extrair dados do Oracle TRUSTED: %s", str(e))
        raise
    finally:
        src_conn.close()

    if total_processed == 0:
        log.info("Nenhum dado válido para processar.")
        return

    log.info("ETL TRUSTED->REFINED concluída: %s registros processados com sucesso.", total_processed)

def _process_batch_maquina_refined(payload):
    """Processa todos os registros no Oracle REFINED com INSERT direto"""
    insert_sql = """
        INSERT INTO MAQUINA (
            TX_MAQUINA, TX_TIPO, QT_NRDECORES, ID_GRUPOMAQUINA
        ) VALUES (
            :TX_MAQUINA, :TX_TIPO, :QT_NRDECORES, :ID_GRUPOMAQUINA
        )
    """

    dst = _make_oracle_conn_refined()
    try:
        cur = dst.cursor()
        
        # Executa o INSERT
        cur.executemany(insert_sql, payload)
        dst.commit()
        log.info("REFINED <- %s registros inseridos com sucesso.", len(payload))
            
    except Exception as e:
        log.error("Erro ao fazer INSERT no Oracle REFINED: %s", str(e))
        dst.rollback()
        raise
    finally:
        dst.close()

# -----------------
# DAG
# -----------------
with DAG(
    dag_id="etl_trusted_to_refined_maquina",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "trusted", "refined", "maquina"],
    default_args={
        'retries': 2,
    }
):
    trusted_to_refined = PythonOperator(
        task_id="trusted_to_refined_maquina",
        python_callable=etl_maquina_trusted_to_refined,
    )