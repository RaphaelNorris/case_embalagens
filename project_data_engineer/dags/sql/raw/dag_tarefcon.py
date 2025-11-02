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

def _map_row_to_oracle_tarefcon(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeamento das colunas do SQL Server para Oracle para a tabela TAREFCON.
    """
    return {
        "MAQUINA": row.get("Maquina"),
        "TAREFA": row.get("Tarefa"),
        "FLAGPARADA": row.get("FlagParada"),
        "CODIGOPARADAOUCONV": row.get("CodigoParadaOUConv"),
        "TURMA": row.get("Turma"),
        "OP": row.get("OP"),
        "PEDIDO": row.get("Pedido"),
        "ITEM": row.get("Item"),
        "REPROGRAMACAO": row.get("Reprogramacao"),
        "PASSAGENS": row.get("Passagens"),
        "OPERACAO": row.get("Operacao"),
        "ARRANJO": row.get("Arranjo"),
        "GRAMATURA": row.get("Gramatura"),
        "QUANTIDADEPROGRAMADA": row.get("QuantidadeProgramada"),
        "CHAPASALIMENTADAS": row.get("ChapasAlimentadas"),
        "QUANTIDADEPRODUZIDA": row.get("QuantidadeProduzida"),
        "QUANTIDADEAJUSTE": row.get("QuantidadeAjuste"),
        "DURACAOPREVISTA": row.get("DuracaoPrevista"),
        "INICIO": _convert_to_timestamp(row.get("Inicio")),
        "FIM": _convert_to_timestamp(row.get("Fim")),
        "OBS1": row.get("Obs1"),
        "OBS2": row.get("Obs2"),
        "ACAOCORRETIVATOMADA": row.get("AcaoCorretivaTomada"),
        "CONSOLIDADO": row.get("Consolidado"),
        "DIADATURMA": _convert_to_timestamp(row.get("DiaDaTurma")),
        "IDCLIENTE": row.get("IDCliente"),
        "USUARIO": row.get("Usuario"),
        "DATACRIACAO": _convert_to_timestamp(row.get("DataCriacao")),
        "USUARIOULTALTERACAO": row.get("UsuarioUltAlteracao"),
        "DATAULTIMAALTERACAO": _convert_to_timestamp(row.get("DataUltimaAlteracao")),
        "CAIXASSEMCOLA": row.get("CaixasSemCola"),
        "ORIGEMREGISTRO": row.get("OrigemRegistro"),
        "DESCORIGEMREGISTRO": row.get("DescOrigemRegistro"),
        "SKIPFEED": row.get("SkipFeed"),
        "OPONDULADA": row.get("OPOndulada"),
        "TAREFAPRODUCAO": row.get("TarefaProducao"),
        "REFILEDIRETOPRENSA": _bit_to_char(row.get("RefileDiretoPrensa")),
        "DURACAO": row.get("Duracao"),
        "IDSECAOMAQUINAPARADA": row.get("IDSecaoMaquinaParada"),
        "FACA": row.get("Faca"),
        "OBSFILA1": row.get("ObsFila1"),
        "OBSFILA2": row.get("ObsFila2"),
        "PRIORIZARPALTEAUTOMESTEIRA": _bit_to_char(row.get("PriorizarPaleteAutomesteira")),
        "IDCODDESTAUTOMESTEIRA": row.get("IDCodDestAutomesteira"),
    }

# -----------------
# Tarefa principal
# -----------------
def etl_tarefcon(**context):
    # CONFIGURAÇÃO PARA TESTE: APENAS 2 LOTES
    # Para executar todos os lotes, comente a linha abaixo e 
    # modifique o while para: while True:
    #max_batches = 2
    
    # Configuração de paginação
    page_size = 20000
    offset = 0
    total_processed = 0
    batch_count = 0
    
    # 1) TRUNCATE na tabela de destino antes da carga
    log.info("Oracle -> Executando TRUNCATE na tabela TAREFCON...")
    dst_conn = _make_oracle_conn()
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

    # ═════════════════════════════════════════════════════════════════════════
    # EXECUÇÃO DE TESTE (apenas 2 lotes):
    # ═════════════════════════════════════════════════════════════════════════
    
    while True: #batch_count < max_batches:  # ⬅️ Modificar para 'while True:' para execução completa

        # Query com paginação
        sql = f"""
            SELECT * FROM TAREFCON 
            ORDER BY MAQUINA, TAREFA
            OFFSET {offset} ROWS 
            FETCH NEXT {page_size} ROWS ONLY
        """
        
        src_conn = _make_mssql_conn()
        try:
            with src_conn.cursor() as cur:
                cur.execute(sql)
                columns = [column[0] for column in cur.description]
                rows = []
                for row in cur.fetchall():
                    rows.append(dict(zip(columns, row)))
            
            log.info("SQL Server -> Página %s: %s registros extraídos da tabela TAREFCON.", 
                    batch_count + 1, len(rows))

            if not rows:
                log.info("Todas as páginas processadas. Total: %s registros.", total_processed)
                break

            # 2) Mapeia para o layout do Oracle
            payload: List[Dict[str, Any]] = []
            for r in rows:
                try:
                    mapped_row = _map_row_to_oracle_tarefcon(r)
                    payload.append(mapped_row)
                except Exception as e:
                    log.warning("Erro ao mapear linha: %s. Linha ignorada.", str(e))
                    continue

            if payload:
                # 3) Processa o lote atual (INSERT no Oracle)
                _process_batch_tarefcon(payload, batch_count + 1)
                total_processed += len(payload)
                log.info("Página %s processada: %s registros válidos (total acumulado: %s)", 
                        batch_count + 1, len(payload), total_processed)
            else:
                log.info("Página %s sem registros válidos, pulando.", batch_count + 1)

            # Prepara próxima página
            batch_count += 1
            offset += page_size
            
            # Limpa memória
            del rows
            del payload

        except Exception as e:
            log.error("Erro ao extrair dados do SQL Server (página %s): %s", batch_count + 1, str(e))
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
            MAQUINA, TAREFA, FLAGPARADA, CODIGOPARADAOUCONV, TURMA, OP, PEDIDO, ITEM,
            REPROGRAMACAO, PASSAGENS, OPERACAO, ARRANJO, GRAMATURA, QUANTIDADEPROGRAMADA,
            CHAPASALIMENTADAS, QUANTIDADEPRODUZIDA, QUANTIDADEAJUSTE, DURACAOPREVISTA,
            INICIO, FIM, OBS1, OBS2, ACAOCORRETIVATOMADA, CONSOLIDADO, DIADATURMA,
            IDCLIENTE, USUARIO, DATACRIACAO, USUARIOULTALTERACAO, DATAULTIMAALTERACAO,
            CAIXASSEMCOLA, ORIGEMREGISTRO, DESCORIGEMREGISTRO, SKIPFEED, OPONDULADA,
            TAREFAPRODUCAO, REFILEDIRETOPRENSA, DURACAO, IDSECAOMAQUINAPARADA, FACA,
            OBSFILA1, OBSFILA2, PRIORIZARPALTEAUTOMESTEIRA, IDCODDESTAUTOMESTEIRA
        ) VALUES (
            :MAQUINA, :TAREFA, :FLAGPARADA, :CODIGOPARADAOUCONV, :TURMA, :OP, :PEDIDO, :ITEM,
            :REPROGRAMACAO, :PASSAGENS, :OPERACAO, :ARRANJO, :GRAMATURA, :QUANTIDADEPROGRAMADA,
            :CHAPASALIMENTADAS, :QUANTIDADEPRODUZIDA, :QUANTIDADEAJUSTE, :DURACAOPREVISTA,
            :INICIO, :FIM, :OBS1, :OBS2, :ACAOCORRETIVATOMADA, :CONSOLIDADO, :DIADATURMA,
            :IDCLIENTE, :USUARIO, :DATACRIACAO, :USUARIOULTALTERACAO, :DATAULTIMAALTERACAO,
            :CAIXASSEMCOLA, :ORIGEMREGISTRO, :DESCORIGEMREGISTRO, :SKIPFEED, :OPONDULADA,
            :TAREFAPRODUCAO, :REFILEDIRETOPRENSA, :DURACAO, :IDSECAOMAQUINAPARADA, :FACA,
            :OBSFILA1, :OBSFILA2, :PRIORIZARPALTEAUTOMESTEIRA, :IDCODDESTAUTOMESTEIRA
        )
    """

    dst = _make_oracle_conn()
    try:
        cur = dst.cursor()
        
        # Configurar inputs específicos para TIMESTAMP
        for param in payload:
            for date_field in ['INICIO', 'FIM', 'DIADATURMA', 'DATACRIACAO', 'DATAULTIMAALTERACAO']:
                if date_field in param and isinstance(param[date_field], datetime):
                    # Garantir que temos microssegundos para TIMESTAMP
                    if param[date_field].microsecond == 0:
                        # Se não tem microssegundos, adiciona alguns para preencher
                        param[date_field] = param[date_field].replace(microsecond=123456)
        
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
    dag_id="etl_tarefcon",
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