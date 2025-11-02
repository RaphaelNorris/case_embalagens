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
ORACLE_CONN_ID_RAW = "oracle_raw"
ORACLE_CONN_ID_TRUSTED = "oracle_trusted"

log = LoggingMixin().log

# -----------------
# Helpers/conexões
# -----------------
def _make_oracle_conn_raw():
    """
    Conecta no Oracle via oracledb usando a Connection do Airflow (oracle_raw).
    """
    c = BaseHook.get_connection(ORACLE_CONN_ID_RAW)
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

# -----------------
# Converters/mapeamentos
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
            return None
    
    try:
        return datetime.combine(value, datetime.min.time())
    except Exception:
        return None

def _map_row_to_oracle_tarefcon(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeamento CORRIGIDO - usando os nomes reais das colunas do Oracle RAW
    """
    # DEBUG: Log para verificar a estrutura dos dados
    if not hasattr(_map_row_to_oracle_tarefcon, 'logged_structure'):
        log.info("Estrutura da linha recebida: %s", list(row.keys())[:10])
        _map_row_to_oracle_tarefcon.logged_structure = True
    
    return {
        "ID_MAQUINA": row.get("MAQUINA") or row.get("Maquina"),
        "CD_TAREFA": row.get("TAREFA") or row.get("Tarefa"),
        "FL_PARADA": row.get("FLAGPARADA") or row.get("FlagParada"),
        "CD_PARADAOUCONV": row.get("CODIGOPARADAOUCONV") or row.get("CodigoParadaOUConv"),
        "TX_TURMA": row.get("TURMA") or row.get("Turma"),
        "TX_OP": row.get("OP") or row.get("OP"),
        "ID_PEDIDO": row.get("PEDIDO") or row.get("Pedido"),
        "ID_ITEM": row.get("ITEM") or row.get("Item"),
        "VL_REPROGRAMACAO": row.get("REPROGRAMACAO") or row.get("Reprogramacao"),
        "VL_PASSAGENS": row.get("PASSAGENS") or row.get("Passagens"),
        "QT_ARRANJO": row.get("ARRANJO") or row.get("Arranjo"),
        "VL_GRAMATURA": row.get("GRAMATURA") or row.get("Gramatura"),
        "QT_PROGRAMADA": row.get("QUANTIDADEPROGRAMADA") or row.get("QuantidadeProgramada"),
        "VL_CHAPASALIMENTADAS": row.get("CHAPASALIMENTADAS") or row.get("ChapasAlimentadas"),
        "QT_PRODUZIDA": row.get("QUANTIDADEPRODUZIDA") or row.get("QuantidadeProduzida"),
        "QT_AJUSTE": row.get("QUANTIDADEAJUSTE") or row.get("QuantidadeAjuste"),
        "VL_DURACAOPREVISTA": row.get("DURACAOPREVISTA") or row.get("DuracaoPrevista"),
        "DT_INICIO": _convert_to_timestamp(row.get("INICIO") or row.get("Inicio")),
        "DT_FIM": _convert_to_timestamp(row.get("FIM") or row.get("Fim")),
        "DT_DIADATURMA": _convert_to_timestamp(row.get("DIADATURMA") or row.get("DiaDaTurma")),
        "ID_CLIENTE": row.get("IDCLIENTE") or row.get("IDCliente"),
        "ID_USUARIO": row.get("USUARIO") or row.get("Usuario"),
        "DT_CRIACAO": _convert_to_timestamp(row.get("DATACRIACAO") or row.get("DataCriacao")),
        "VL_USUARIOULTALTERACAO": row.get("USUARIOULTALTERACAO") or row.get("UsuarioUltAlteracao"),
        "DT_ULTIMAALTERACAO": _convert_to_timestamp(row.get("DATAULTIMAALTERACAO") or row.get("DataUltimaAlteracao")),
        "VL_ORIGEMREGISTRO": row.get("ORIGEMREGISTRO") or row.get("OrigemRegistro"),
        "TX_DESCORIGEMREGISTRO": row.get("DESCORIGEMREGISTRO") or row.get("DescOrigemRegistro"),
        "FL_SKIPFEED": row.get("SKIPFEED") or row.get("SkipFeed"),
        "TX_OPONDULADA": row.get("OPONDULADA") or row.get("OPOndulada"),
        "VL_TAREFAPRODUCAO": row.get("TAREFAPRODUCAO") or row.get("TarefaProducao"),
        "FL_REFILEDIRETOPRENSA": _bit_to_char(row.get("REFILEDIRETOPRENSA") or row.get("RefileDiretoPrensa")),
        "VL_DURACAO": row.get("DURACAO") or row.get("Duracao"),
        "ID_SECAOMAQUINAPARADA": row.get("IDSECAOMAQUINAPARADA") or row.get("IDSecaoMaquinaParada"),
        "CD_FACA": row.get("FACA") or row.get("Faca")
    }

# -----------------
# Tarefa principal
# -----------------
def etl_tarefcon(**context):
    # Configuração de paginação - 40.000 registros por lote
    page_size = 20000
    offset = 0
    total_processed = 0
    batch_count = 0
    
    # 1) TRUNCATE na tabela de destino
    log.info("Oracle -> Executando TRUNCATE na tabela TAREFCON...")
    dst_conn = _make_oracle_conn_trusted()
    try:
        with dst_conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE TAREFCON")
        dst_conn.commit()
        log.info("Oracle -> TRUNCATE executado com sucesso na tabela TAREFCON.")
    except Exception as e:
        log.error("Erro ao executar TRUNCATE no Oracle: %s", str(e))
        dst_conn.rollback()
        raise
    finally:
        dst_conn.close()

    # Loop de paginação
    while True:
        # Query com paginação usando bind variables
        sql = """
            SELECT * FROM TAREFCON 
            ORDER BY MAQUINA, TAREFA
            OFFSET :offset ROWS 
            FETCH NEXT :page_size ROWS ONLY
        """
        
        src_conn = _make_oracle_conn_raw()
        try:
            with src_conn.cursor() as cur:
                cur.execute(sql, offset=offset, page_size=page_size)
                columns = [column[0] for column in cur.description]
                rows = []
                for row in cur.fetchall():
                    rows.append(dict(zip(columns, row)))
            
            log.info("RAW -> Página %s: %s registros extraídos da tabela TAREFCON.", 
                    batch_count + 1, len(rows))

            if not rows:
                log.info("Todas as páginas processadas. Total: %s registros.", total_processed)
                break

            # 2) Mapeia para o layout do Oracle
            payload = []
            mapping_errors = 0
            
            for r in rows:
                try:
                    mapped_row = _map_row_to_oracle_tarefcon(r)
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
                    log.info("Primeiro registro mapeado: %s", {k: v for k, v in list(payload[0].items())[:5]})
                
                # 3) Processa o lote atual
                _process_batch_tarefcon(payload, batch_count + 1)
                total_processed += len(payload)
                log.info("Página %s processada: %s registros válidos (total acumulado: %s)", 
                        batch_count + 1, len(payload), total_processed)
            else:
                log.info("Página %s sem registros válidos, pulando.", batch_count + 1)

            # Prepara próxima página
            batch_count += 1
            offset += page_size
            
        except Exception as e:
            log.error("Erro ao extrair dados do Oracle RAW (página %s): %s", batch_count + 1, str(e))
            raise
        finally:
            src_conn.close()

    if total_processed == 0:
        log.info("Nenhum dado válido para processar.")
        return

    log.info("ETL concluída: %s registros processados com sucesso em %s lotes.", total_processed, batch_count)

def _process_batch_tarefcon(payload, batch_number):
    """Processa um lote de registros no Oracle com INSERT direto"""
    insert_sql = """
        INSERT INTO TAREFCON (
            ID_MAQUINA, CD_TAREFA, FL_PARADA, CD_PARADAOUCONV, TX_TURMA, TX_OP, ID_PEDIDO, ID_ITEM,
            VL_REPROGRAMACAO, VL_PASSAGENS, QT_ARRANJO, VL_GRAMATURA, QT_PROGRAMADA,
            VL_CHAPASALIMENTADAS, QT_PRODUZIDA, QT_AJUSTE, VL_DURACAOPREVISTA,
            DT_INICIO, DT_FIM, DT_DIADATURMA,
            ID_CLIENTE, ID_USUARIO, DT_CRIACAO, VL_USUARIOULTALTERACAO, DT_ULTIMAALTERACAO,
            VL_ORIGEMREGISTRO, TX_DESCORIGEMREGISTRO, FL_SKIPFEED, TX_OPONDULADA,
            VL_TAREFAPRODUCAO, FL_REFILEDIRETOPRENSA, VL_DURACAO, ID_SECAOMAQUINAPARADA, CD_FACA
        ) VALUES (
            :ID_MAQUINA, :CD_TAREFA, :FL_PARADA, :CD_PARADAOUCONV, :TX_TURMA, :TX_OP, :ID_PEDIDO, :ID_ITEM,
            :VL_REPROGRAMACAO, :VL_PASSAGENS, :QT_ARRANJO, :VL_GRAMATURA, :QT_PROGRAMADA,
            :VL_CHAPASALIMENTADAS, :QT_PRODUZIDA, :QT_AJUSTE, :VL_DURACAOPREVISTA,
            :DT_INICIO, :DT_FIM, :DT_DIADATURMA,
            :ID_CLIENTE, :ID_USUARIO, :DT_CRIACAO, :VL_USUARIOULTALTERACAO, :DT_ULTIMAALTERACAO,
            :VL_ORIGEMREGISTRO, :TX_DESCORIGEMREGISTRO, :FL_SKIPFEED, :TX_OPONDULADA,
            :VL_TAREFAPRODUCAO, :FL_REFILEDIRETOPRENSA, :VL_DURACAO, :ID_SECAOMAQUINAPARADA, :CD_FACA
        )
    """

    dst = _make_oracle_conn_trusted()
    try:
        cur = dst.cursor()
        
        # Executa o INSERT
        cur.executemany(insert_sql, payload)
        dst.commit()
        log.info("Oracle <- Lote %s: %s registros inseridos com sucesso.", batch_number, len(payload))
            
    except Exception as e:
        log.error("Erro ao fazer INSERT no Oracle (lote %s): %s", batch_number, str(e))
        dst.rollback()
        raise
    finally:
        dst.close()

# -----------------
# DAG
# -----------------
with DAG(
    dag_id="etl_raw_to_trusted_tarefcon",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "sqlserver", "oracle", "tarefcon"],
    default_args={
        'retries': 2,
    }
):
    merge_upsert = PythonOperator(
        task_id="merge_upsert_tarefcon",
        python_callable=etl_tarefcon,
    )