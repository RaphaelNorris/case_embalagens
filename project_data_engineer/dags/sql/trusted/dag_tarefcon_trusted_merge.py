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
    
    # **ALTERAÇÃO: REMOVIDA completamente a limpeza da tabela destino**
    log.info("Iniciando ETL TAREFCON - SEM LIMPEZA DA TABELA DESTINO")
    log.info("Os dados existentes na tabela TAREFCON serão mantidos e atualizados via MERGE")

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
                
                # 3) Processa o lote atual com MERGE
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
    """Processa um lote de registros no Oracle com MERGE (UPSERT)"""
    
    merge_sql = """
        MERGE INTO TAREFCON t 
        USING (SELECT 
            :ID_MAQUINA as ID_MAQUINA,
            :CD_TAREFA as CD_TAREFA,
            :FL_PARADA as FL_PARADA,
            :CD_PARADAOUCONV as CD_PARADAOUCONV,
            :TX_TURMA as TX_TURMA,
            :TX_OP as TX_OP,
            :ID_PEDIDO as ID_PEDIDO,
            :ID_ITEM as ID_ITEM,
            :VL_REPROGRAMACAO as VL_REPROGRAMACAO,
            :VL_PASSAGENS as VL_PASSAGENS,
            :QT_ARRANJO as QT_ARRANJO,
            :VL_GRAMATURA as VL_GRAMATURA,
            :QT_PROGRAMADA as QT_PROGRAMADA,
            :VL_CHAPASALIMENTADAS as VL_CHAPASALIMENTADAS,
            :QT_PRODUZIDA as QT_PRODUZIDA,
            :QT_AJUSTE as QT_AJUSTE,
            :VL_DURACAOPREVISTA as VL_DURACAOPREVISTA,
            :DT_INICIO as DT_INICIO,
            :DT_FIM as DT_FIM,
            :DT_DIADATURMA as DT_DIADATURMA,
            :ID_CLIENTE as ID_CLIENTE,
            :ID_USUARIO as ID_USUARIO,
            :DT_CRIACAO as DT_CRIACAO,
            :VL_USUARIOULTALTERACAO as VL_USUARIOULTALTERACAO,
            :DT_ULTIMAALTERACAO as DT_ULTIMAALTERACAO,
            :VL_ORIGEMREGISTRO as VL_ORIGEMREGISTRO,
            :TX_DESCORIGEMREGISTRO as TX_DESCORIGEMREGISTRO,
            :FL_SKIPFEED as FL_SKIPFEED,
            :TX_OPONDULADA as TX_OPONDULADA,
            :VL_TAREFAPRODUCAO as VL_TAREFAPRODUCAO,
            :FL_REFILEDIRETOPRENSA as FL_REFILEDIRETOPRENSA,
            :VL_DURACAO as VL_DURACAO,
            :ID_SECAOMAQUINAPARADA as ID_SECAOMAQUINAPARADA,
            :CD_FACA as CD_FACA
        FROM dual) s 
        ON (t.ID_MAQUINA = s.ID_MAQUINA AND t.CD_TAREFA = s.CD_TAREFA AND t.ID_PEDIDO = s.ID_PEDIDO AND t.ID_ITEM = s.ID_ITEM)
        WHEN MATCHED THEN UPDATE SET 
            t.FL_PARADA = s.FL_PARADA,
            t.CD_PARADAOUCONV = s.CD_PARADAOUCONV,
            t.TX_TURMA = s.TX_TURMA,
            t.TX_OP = s.TX_OP,
            t.VL_REPROGRAMACAO = s.VL_REPROGRAMACAO,
            t.VL_PASSAGENS = s.VL_PASSAGENS,
            t.QT_ARRANJO = s.QT_ARRANJO,
            t.VL_GRAMATURA = s.VL_GRAMATURA,
            t.QT_PROGRAMADA = s.QT_PROGRAMADA,
            t.VL_CHAPASALIMENTADAS = s.VL_CHAPASALIMENTADAS,
            t.QT_PRODUZIDA = s.QT_PRODUZIDA,
            t.QT_AJUSTE = s.QT_AJUSTE,
            t.VL_DURACAOPREVISTA = s.VL_DURACAOPREVISTA,
            t.DT_INICIO = s.DT_INICIO,
            t.DT_FIM = s.DT_FIM,
            t.DT_DIADATURMA = s.DT_DIADATURMA,
            t.ID_CLIENTE = s.ID_CLIENTE,
            t.ID_USUARIO = s.ID_USUARIO,
            t.DT_CRIACAO = s.DT_CRIACAO,
            t.VL_USUARIOULTALTERACAO = s.VL_USUARIOULTALTERACAO,
            t.DT_ULTIMAALTERACAO = s.DT_ULTIMAALTERACAO,
            t.VL_ORIGEMREGISTRO = s.VL_ORIGEMREGISTRO,
            t.TX_DESCORIGEMREGISTRO = s.TX_DESCORIGEMREGISTRO,
            t.FL_SKIPFEED = s.FL_SKIPFEED,
            t.TX_OPONDULADA = s.TX_OPONDULADA,
            t.VL_TAREFAPRODUCAO = s.VL_TAREFAPRODUCAO,
            t.FL_REFILEDIRETOPRENSA = s.FL_REFILEDIRETOPRENSA,
            t.VL_DURACAO = s.VL_DURACAO,
            t.ID_SECAOMAQUINAPARADA = s.ID_SECAOMAQUINAPARADA,
            t.CD_FACA = s.CD_FACA
        WHEN NOT MATCHED THEN INSERT (
            ID_MAQUINA, CD_TAREFA, FL_PARADA, CD_PARADAOUCONV, TX_TURMA, TX_OP, ID_PEDIDO, ID_ITEM,
            VL_REPROGRAMACAO, VL_PASSAGENS, QT_ARRANJO, VL_GRAMATURA, QT_PROGRAMADA,
            VL_CHAPASALIMENTADAS, QT_PRODUZIDA, QT_AJUSTE, VL_DURACAOPREVISTA,
            DT_INICIO, DT_FIM, DT_DIADATURMA,
            ID_CLIENTE, ID_USUARIO, DT_CRIACAO, VL_USUARIOULTALTERACAO, DT_ULTIMAALTERACAO,
            VL_ORIGEMREGISTRO, TX_DESCORIGEMREGISTRO, FL_SKIPFEED, TX_OPONDULADA,
            VL_TAREFAPRODUCAO, FL_REFILEDIRETOPRENSA, VL_DURACAO, ID_SECAOMAQUINAPARADA, CD_FACA
        ) VALUES (
            s.ID_MAQUINA, s.CD_TAREFA, s.FL_PARADA, s.CD_PARADAOUCONV, s.TX_TURMA, s.TX_OP, s.ID_PEDIDO, s.ID_ITEM,
            s.VL_REPROGRAMACAO, s.VL_PASSAGENS, s.QT_ARRANJO, s.VL_GRAMATURA, s.QT_PROGRAMADA,
            s.VL_CHAPASALIMENTADAS, s.QT_PRODUZIDA, s.QT_AJUSTE, s.VL_DURACAOPREVISTA,
            s.DT_INICIO, s.DT_FIM, s.DT_DIADATURMA,
            s.ID_CLIENTE, s.ID_USUARIO, s.DT_CRIACAO, s.VL_USUARIOULTALTERACAO, s.DT_ULTIMAALTERACAO,
            s.VL_ORIGEMREGISTRO, s.TX_DESCORIGEMREGISTRO, s.FL_SKIPFEED, s.TX_OPONDULADA,
            s.VL_TAREFAPRODUCAO, s.FL_REFILEDIRETOPRENSA, s.VL_DURACAO, s.ID_SECAOMAQUINAPARADA, s.CD_FACA
        )
    """

    dst = _make_oracle_conn_trusted()
    try:
        cur = dst.cursor()
        
        # Executa o MERGE
        cur.executemany(merge_sql, payload)
        dst.commit()
        log.info("TRUSTED <- Lote %s: %s registros processados com MERGE (UPSERT).", batch_number, len(payload))
            
    except Exception as e:
        log.error("Erro ao fazer MERGE no Oracle (lote %s): %s", batch_number, str(e))
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