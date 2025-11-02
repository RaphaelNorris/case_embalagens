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
    Campos FL_ retornam "0" ou "1" (VARCHAR2(1)).
    """
    # Se for campo FL_, converte para "0" ou "1"
    if field_name and field_name.startswith('FL_'):
        if value is None:
            return "0"
        
        # Converte qualquer valor para "0" ou "1"
        if isinstance(value, bool):
            return "1" if value else "0"
        elif isinstance(value, int):
            return "1" if value != 0 else "0"
        elif isinstance(value, str):
            value_clean = value.strip().upper()
            # Considera como True: "1", "Y", "S", "TRUE", "T", "SIM"
            if value_clean in ("1", "Y", "S", "TRUE", "T", "SIM"):
                return "1"
            # Considera como False: "0", "N", "FALSE", "F", "NAO", "NÃO"
            elif value_clean in ("0", "N", "FALSE", "F", "NAO", "NÃO"):
                return "0"
            else:
                # Para outras strings, tenta converter para número
                try:
                    num_val = int(value)
                    return "1" if num_val != 0 else "0"
                except ValueError:
                    # Se string não vazia, considera como True
                    return "1" if value_clean != "" else "0"
        elif isinstance(value, bytes):
            # Se já é bytes, verifica se não é zero
            if value == b'\x00' or value == b'':
                return "0"
            else:
                return "1"
        else:
            # Para outros tipos (float, etc), converte para booleano
            return "1" if bool(value) else "0"
    
    # Se for campo TX_, força retorno de string vazia para NULL
    elif field_name and field_name.startswith('TX_'):
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

def _convert_to_timestamp(value, nan_date=None):
    """
    Converte para TIMESTAMP do Oracle. Para NaN, retorna data padrão.
    """
    if value is None:
        if nan_date == "2999/01/01":
            return datetime(2999, 1, 1)
        return None
    
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, str):
        try:
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
            from dateutil import parser
            return parser.parse(value)
        except Exception as e:
            log.warning("Não foi possível converter data '%s': %s", value, str(e))
            if nan_date == "2999/01/01":
                return datetime(2999, 1, 1)
            return None
    
    try:
        return datetime.combine(value, datetime.min.time())
    except Exception:
        if nan_date == "2999/01/01":
            return datetime(2999, 1, 1)
        return None

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

def _map_row_to_refined_tarefcon(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeamento da TRUSTED para REFINED com conversões de tipo e tratamento de NaN.
    """
    # DEBUG: Log para verificar a estrutura dos dados
    if not hasattr(_map_row_to_refined_tarefcon, 'logged_structure'):
        log.info("Estrutura da linha recebida da TRUSTED: %s", list(row.keys())[:10])
        _map_row_to_refined_tarefcon.logged_structure = True
    
    return {
        "ID_MAQUINA": _convert_to_varchar(row.get("ID_MAQUINA") or row.get("MAQUINA"), "-1", "ID_MAQUINA"),
        "FL_PARADA": _convert_to_varchar(_handle_nan(row.get("FL_PARADA") or row.get("PARADA"), 0), "0", "FL_PARADA"),
        "CD_PARADAOUCONV": _convert_to_varchar(row.get("CD_PARADAOUCONV") or row.get("PARADAOUCONV"), "-1", "CD_PARADAOUCONV"),
        "TX_TURMA": _convert_to_varchar(row.get("TX_TURMA") or row.get("TURMA"), "", "TX_TURMA"),
        "TX_OP": _convert_to_varchar(row.get("TX_OP") or row.get("OP"), "", "TX_OP"),
        "ID_PEDIDO": _convert_to_varchar(row.get("ID_PEDIDO") or row.get("PEDIDO"), "-1", "ID_PEDIDO"),
        "ID_ITEM": _convert_to_varchar(row.get("ID_ITEM") or row.get("ITEM"), "-1", "ID_ITEM"),
        "VL_REPROGRAMACAO": _convert_to_number(row.get("VL_REPROGRAMACAO") or row.get("REPROGRAMACAO"), 0),
        "QT_ARRANJO": _convert_to_number(row.get("QT_ARRANJO") or row.get("ARRANJO"), 0),
        "VL_GRAMATURA": _convert_to_number(row.get("VL_GRAMATURA") or row.get("GRAMATURA"), 0),
        "QT_PROGRAMADA": _convert_to_number(row.get("QT_PROGRAMADA") or row.get("PROGRAMADA"), 0),
        "VL_CHAPASALIMENTADAS": _convert_to_number(row.get("VL_CHAPASALIMENTADAS") or row.get("CHAPASALIMENTADAS"), 0),
        "QT_PRODUZIDA": _convert_to_number(row.get("QT_PRODUZIDA") or row.get("PRODUZIDA"), 0),
        "QT_AJUSTE": _convert_to_number(row.get("QT_AJUSTE") or row.get("AJUSTE"), 0),
        "VL_DURACAOPREVISTA": _convert_to_number(row.get("VL_DURACAOPREVISTA") or row.get("DURACAOPREVISTA"), 0),
        "DT_INICIO": _convert_to_timestamp(row.get("DT_INICIO") or row.get("INICIO"), "2999/01/01"),
        "DT_FIM": _convert_to_timestamp(row.get("DT_FIM") or row.get("FIM"), "2999/01/01"),
        "DT_DIADATURMA": _convert_to_timestamp(row.get("DT_DIADATURMA") or row.get("DIADATURMA"), "2999/01/01"),
        "ID_CLIENTE": _convert_to_varchar(row.get("ID_CLIENTE") or row.get("CLIENTE"), "-1", "ID_CLIENTE"),
        "ID_USUARIO": _convert_to_varchar(row.get("ID_USUARIO") or row.get("USUARIO"), "-1", "ID_USUARIO"),
        "VL_ORIGEMREGISTRO": _convert_to_number(row.get("VL_ORIGEMREGISTRO") or row.get("ORIGEMREGISTRO"), 0),
        "TX_DESCORIGEMREGISTRO": _convert_to_varchar(row.get("TX_DESCORIGEMREGISTRO") or row.get("DESCORIGEMREGISTRO"), "", "TX_DESCORIGEMREGISTRO"),
        "FL_SKIPFEED": _convert_to_varchar(_handle_nan(row.get("FL_SKIPFEED") or row.get("SKIPFEED"), 0), "0", "FL_SKIPFEED"),
        "TX_OPONDULADA": _convert_to_varchar(row.get("TX_OPONDULADA") or row.get("OPONDULADA"), "", "TX_OPONDULADA"),
        "VL_DURACAO": _convert_to_number(row.get("VL_DURACAO") or row.get("DURACAO"), 0),
        "CD_FACA": _convert_to_varchar(row.get("CD_FACA") or row.get("FACA"), "-1", "CD_FACA")
    }
# -----------------
# Tarefa principal
# -----------------
def etl_tarefcon_trusted_to_refined(**context):
    # Configuração de paginação - 40.000 registros por lote
    page_size = 40000
    offset = 0
    total_processed = 0
    batch_count = 0
    
    # 1) TRUNCATE na tabela de destino REFINED
    log.info("REFINED -> Executando TRUNCATE na tabela TAREFCON...")
    dst_conn = _make_oracle_conn_refined()
    try:
        with dst_conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE TAREFCON")
        dst_conn.commit()
        log.info("REFINED -> TRUNCATE executado com sucesso na tabela TAREFCON.")
    except Exception as e:
        log.error("Erro ao executar TRUNCATE no Oracle REFINED: %s", str(e))
        dst_conn.rollback()
        raise
    finally:
        dst_conn.close()

    # Loop de paginação
    while True:
        # Query com paginação da tabela TRUSTED
        sql = """
            SELECT * FROM TAREFCON 
            ORDER BY ID_MAQUINA, CD_TAREFA
            OFFSET :offset ROWS 
            FETCH NEXT :page_size ROWS ONLY
        """
        
        src_conn = _make_oracle_conn_trusted()
        try:
            with src_conn.cursor() as cur:
                cur.execute(sql, offset=offset, page_size=page_size)
                columns = [column[0] for column in cur.description]
                rows = []
                for row in cur.fetchall():
                    rows.append(dict(zip(columns, row)))
            
            log.info("TRUSTED -> Página %s: %s registros extraídos da tabela TAREFCON.", 
                    batch_count + 1, len(rows))

            if not rows:
                log.info("Todas as páginas processadas. Total: %s registros.", total_processed)
                break

            # 2) Mapeia para o layout do REFINED
            payload = []
            mapping_errors = 0
            
            for r in rows:
                try:
                    mapped_row = _map_row_to_refined_tarefcon(r)
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
                log.warning("Página %s: %s registros com erro de mapeamento", batch_count + 1, mapping_errors)

            if payload:
                # DEBUG: Mostrar primeiro registro mapeado
                if batch_count == 0 and payload:
                    log.info("Primeiro registro mapeado para REFINED: %s", {k: v for k, v in list(payload[0].items())[:5]})
                
                # 3) Processa o lote atual
                _process_batch_tarefcon_refined(payload, batch_count + 1)
                total_processed += len(payload)
                log.info("Página %s processada: %s registros válidos (total acumulado: %s)", 
                        batch_count + 1, len(payload), total_processed)
            else:
                log.info("Página %s sem registros válidos, pulando.", batch_count + 1)

            # Prepara próxima página
            batch_count += 1
            offset += page_size
            
        except Exception as e:
            log.error("Erro ao extrair dados do Oracle TRUSTED (página %s): %s", batch_count + 1, str(e))
            raise
        finally:
            src_conn.close()

    if total_processed == 0:
        log.info("Nenhum dado válido para processar.")
        return

    log.info("ETL TRUSTED->REFINED concluída: %s registros processados com sucesso em %s lotes.", total_processed, batch_count)

def _process_batch_tarefcon_refined(payload, batch_number):
    """Processa um lote de registros no Oracle REFINED com INSERT direto"""
    insert_sql = """
        INSERT INTO TAREFCON (
            ID_MAQUINA, FL_PARADA, CD_PARADAOUCONV, TX_TURMA, TX_OP, ID_PEDIDO, ID_ITEM,
            VL_REPROGRAMACAO, QT_ARRANJO, VL_GRAMATURA, QT_PROGRAMADA,
            VL_CHAPASALIMENTADAS, QT_PRODUZIDA, QT_AJUSTE, VL_DURACAOPREVISTA,
            DT_INICIO, DT_FIM, DT_DIADATURMA,
            ID_CLIENTE, ID_USUARIO, VL_ORIGEMREGISTRO, TX_DESCORIGEMREGISTRO, 
            FL_SKIPFEED, TX_OPONDULADA, VL_DURACAO, CD_FACA
        ) VALUES (
            :ID_MAQUINA, :FL_PARADA, :CD_PARADAOUCONV, :TX_TURMA, :TX_OP, :ID_PEDIDO, :ID_ITEM,
            :VL_REPROGRAMACAO, :QT_ARRANJO, :VL_GRAMATURA, :QT_PROGRAMADA,
            :VL_CHAPASALIMENTADAS, :QT_PRODUZIDA, :QT_AJUSTE, :VL_DURACAOPREVISTA,
            :DT_INICIO, :DT_FIM, :DT_DIADATURMA,
            :ID_CLIENTE, :ID_USUARIO, :VL_ORIGEMREGISTRO, :TX_DESCORIGEMREGISTRO,
            :FL_SKIPFEED, :TX_OPONDULADA, :VL_DURACAO, :CD_FACA
        )
    """

    dst = _make_oracle_conn_refined()
    try:
        cur = dst.cursor()
        
        # Executa o INSERT
        cur.executemany(insert_sql, payload)
        dst.commit()
        log.info("REFINED <- Lote %s: %s registros inseridos com sucesso.", batch_number, len(payload))
            
    except Exception as e:
        log.error("Erro ao fazer INSERT no Oracle REFINED (lote %s): %s", batch_number, str(e))
        dst.rollback()
        raise
    finally:
        dst.close()

# -----------------
# DAG
# -----------------
with DAG(
    dag_id="etl_trusted_to_refined_tarefcon",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "trusted", "refined", "tarefcon"],
    default_args={
        'retries': 2,
    }
):
    trusted_to_refined = PythonOperator(
        task_id="trusted_to_refined_tarefcon",
        python_callable=etl_tarefcon_trusted_to_refined,
    )