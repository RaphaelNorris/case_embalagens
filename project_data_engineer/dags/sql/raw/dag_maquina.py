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
# Converters/mapeamentos para MAQUINA
# -----------------
def _bit_to_char(v: Any) -> str:
    if v is None:
        return "N"
    return "Y" if v in (1, True, "1", "Y", "y") else "N"

def _number_to_int(v: Any) -> int:
    """
    Converte valor para inteiro.
    """
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None
    

def _convert_to_timestamp(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S']:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        except Exception:
            return None
    try:
        return datetime.combine(value, datetime.min.time())
    except Exception:
        return None

def _map_row_to_oracle_maquina(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeamento das colunas do SQL Server para Oracle para a tabela MAQUINA.
    """
    return {
        "MAQ_ID": _number_to_int(row.get("MAQ_Id")),
        "MAQUINA": row.get("Maquina"),
        "NOMEMAQUINA": row.get("NomeMaquina"),
        "TIPO": _number_to_int(row.get("Tipo")),
        "FACOES": _number_to_int(row.get("Facoes")),
        "LARGUTILMAX": _number_to_int(row.get("LargUtilMax")),
        "LARGMINCHAPA": _number_to_int(row.get("LargMinChapa")),
        "LARGMAXCHAPA": _number_to_int(row.get("LargMaxChapa")),
        "COMPMINCHAPA": _number_to_int(row.get("CompMinChapa")),
        "COMPMAXCHAPA": _number_to_int(row.get("CompMaxChapa")),
        "REFILOMIN": _number_to_int(row.get("RefiloMin")),
        "REFILOMAX": _number_to_int(row.get("RefiloMax")),
        "FACAS": _number_to_int(row.get("Facas")),
        "PERMITEMISTURARFERRAMENTAS": _bit_to_char(row.get("PermiteMisturarFerramentas")),
        "IDTIPOVINCOPADRAO": _number_to_int(row.get("IDTipoVincoPadrao")),
        "TEARTAPE": _number_to_int(row.get("TearTape")),
        "RESINAINTERNA": _number_to_int(row.get("ResinaInterna")),
        "RESINAEXTERNA": _number_to_int(row.get("ResinaExterna")),
        "ENDURECEDORMIOLO": _number_to_int(row.get("EndurecedorMiolo")),
        "ROTACAOMAXIMA": row.get("RotacaoMaxima"),
        "CUSTOHORA": row.get("CustoHora"),
        "CUSTOMETRO": row.get("CustoMetro"),
        "CUSTOMETROQUAD": row.get("CustoMetroQuad"),
        "FORMATOPADRAO": row.get("FormatoPadrao"),
        "UNIDPRODUTIVIDADE": _number_to_int(row.get("UnidProdutividade")),
        "DESCUNIDPRODUTIVIDADE": row.get("DescUnidProdutividade"),
        "SETUP": _number_to_int(row.get("Setup")),
        "PRODM2": _number_to_int(row.get("ProdM2")),
        "PRODBATIDAS": _number_to_int(row.get("ProdBatidas")),
        "PRODKG": _number_to_int(row.get("ProdKg")),
        "PRODMAQUINA": _number_to_int(row.get("ProdMaquina")),
        "HOMENSTURMA": _number_to_int(row.get("HomensTurma")),
        "GANTT": _number_to_int(row.get("Gantt")),
        "NRDECORES": _number_to_int(row.get("NrDeCores")),
        "LOGGANTT": _number_to_int(row.get("LogGantt")),
        "COMPMINCONJ": _number_to_int(row.get("CompMinConj")),
        "IDGRUPOMAQUINA": _number_to_int(row.get("IDGrupoMaquina")),
        "PRODUTIVIDADEPADRAO": _number_to_int(row.get("ProdutividadePadrao")),
        "EFICIENCIAPADRAO": _number_to_int(row.get("EficienciaPadrao")),
        "TAREFAATUAL": row.get("TarefaAtual"),
        "INICIOTAREFAATUAL": _convert_to_timestamp(row.get("InicioTarefaAtual")),
        "FIMPREVTAREFAATUAL": _convert_to_timestamp(row.get("FimPrevTarefaAtual")),
        "PARADAATUAL": _number_to_int(row.get("ParadaAtual")),
        "INICIOPARADAATUAL": _convert_to_timestamp(row.get("InicioParadaAtual")),
        "FIMPREVPARADAATUAL": _convert_to_timestamp(row.get("FimPrevParadaAtual")),
        "IDSECAOMAQUINAPARADAATUAL": _number_to_int(row.get("IDSecaoMaquinaParadaAtual")),
        "PROGRAMARPRODUCAO": _bit_to_char(row.get("ProgramarProducao")),
        "DESATIVADA": _number_to_int(row.get("Desativada")),
        "CODIGOERP": row.get("CodigoERP"),
        "PERDALIMITEAVISO": _number_to_int(row.get("PerdaLimiteAviso")),
        "UNIDADEAPONTCONJUGACAO": _number_to_int(row.get("UnidadeApontConjugacao")),
        "TESTEPORBOLETIM": _number_to_int(row.get("TestePorBoletim")),
        "IDJORNADA": _number_to_int(row.get("IDJornada")),
        "DISTMINVINCOS": _number_to_int(row.get("DistMinVincos")),
        "IDCENTROCUSTO": _number_to_int(row.get("IDCentroCusto")),
        "IDCENTROCUSTOMAQ": _number_to_int(row.get("IDCentroCustoMaq")),
        "IDSESSAODB": _number_to_int(row.get("IDSessaoDB")),
        "PORCMINLARGURARESINADA": _number_to_int(row.get("PorcMinLarguraResinada")),
        "CARGAMAQLOTE": _number_to_int(row.get("CargaMaqLote")),
        "VALIDAINTERSECCAOAPONTAMENTO": _number_to_int(row.get("ValidaIntersecaoApontamento")),
        "DESCVALIDAINTERSECCAOAPONT": row.get("DescValidaIntersecaoApont"),
        "VALIDABURACOAPONTAMENTO": _number_to_int(row.get("ValidaBuracoApontamento")),
        "DESCVALIDABURACOAPONTAMENTO": row.get("DescValidaBuracoApontamento"),
        "CONSEGUIREFILARSOMENTEUMLADO": _number_to_int(row.get("ConsegueRefilarSomenteUmLado")),
        "IDUNIDADEFABRIL": _number_to_int(row.get("IDUnidadeFabril")),
        "REFILEDIRETOPRENSA": _bit_to_char(row.get("RefileDiretoPrensa")),
        "AREAM2PERDIDAPORCONJUGACAO": _number_to_int(row.get("AreaM2PerdidaPorConjugacao")),
        "AREAM2PERDIDOTROCAFORMATO": _number_to_int(row.get("AreaM2PerdidaTrocaFormato")),
        "DIFPORCPRODUTMAQFT_MENOS": _number_to_int(row.get("DifPorcProdutividadeMaqFT_Menos")),
        "DIFPORCPRODUTMAQFT_MAIS": _number_to_int(row.get("DifPorcProdutividadeMaqFT_Mais")),
        "PEDIDOMINIMOM2": _number_to_int(row.get("PedidoMinimoM2")),
        "PEDIDOMINIMOKG": _number_to_int(row.get("PedidoMinimoKG")),
        "LIMITAMINIMOACESSORIO": _bit_to_char(row.get("LimitaMinimoAcessorio")),
        "DISPONIVELLOTENOVO": _bit_to_char(row.get("DisponivelLoteNovo")),
        "PERDAPRODUCAOPERC": row.get("PerdaProducaoPerc"),
        "PERDAPRODUCAOPECAS": row.get("PerdaProducaoPecas"),
        "DESLOCMAXIMPORTABOBINAS_MM": _number_to_int(row.get("DeslocMaximoPortaBobinas_MM")),
        "LARGURALIMITEESTABILIDADEPILHA": _number_to_int(row.get("LarguraLimiteEstabilidadePilha")),
        "COMPRIMENTOREFOGOGUILHOTINA": _number_to_int(row.get("ComprimentoRefogoGuilhotina")),
        "HABILITARINTEGRACAOESTEIRAOND": _bit_to_char(row.get("HabilitarIntegracaoEsteiraOnd")),
    }

# -----------------
# Tarefa principal para MAQUINA - REFATORADA (TRUNCATE + INSERT)
# -----------------
def etl_maquina(**context):
    # 1) Extrai do SQL Server
    sql = "SELECT * FROM MAQUINA"
    src_conn = _make_mssql_conn()
    try:
        with src_conn.cursor() as cur:
            cur.execute(sql)
            columns = [column[0] for column in cur.description]
            rows = []
            for row in cur.fetchall():
                rows.append(dict(zip(columns, row)))
        log.info("SQL Server -> %s registros extraídos da tabela MAQUINA.", len(rows))
        
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
            mapped_row = _map_row_to_oracle_maquina(r)
            payload.append(mapped_row)
        except Exception as e:
            log.warning("Erro ao mapear linha: %s. Linha ignorada.", str(e))
            continue

    if not payload:
        log.info("Nenhum dado válido para processar após mapeamento.")
        return

    # 3) TRUNCATE + INSERT no Oracle
    dst = _make_oracle_conn()
    try:
        cur = dst.cursor()
        
        # Primeiro faz o TRUNCATE da tabela
        log.info("Oracle -> Executando TRUNCATE TABLE MAQUINA...")
        cur.execute("TRUNCATE TABLE MAQUINA")
        log.info("Oracle -> Tabela MAQUINA truncada com sucesso.")
        
        # Prepara o INSERT
        insert_sql = """
            INSERT INTO MAQUINA (
                MAQ_ID, MAQUINA, NOMEMAQUINA, TIPO, FACOES, LARGUTILMAX, LARGMINCHAPA,
                LARGMAXCHAPA, COMPMINCHAPA, COMPMAXCHAPA, REFILOMIN, REFILOMAX, FACAS,
                PERMITEMISTURARFERRAMENTAS, IDTIPOVINCOPADRAO, TEARTAPE, RESINAINTERNA, RESINAEXTERNA,
                ENDURECEDORMIOLO, ROTACAOMAXIMA, CUSTOHORA, CUSTOMETRO, CUSTOMETROQUAD, FORMATOPADRAO,
                UNIDPRODUTIVIDADE, DESCUNIDPRODUTIVIDADE, SETUP, PRODM2, PRODBATIDAS, PRODKG,
                PRODMAQUINA, HOMENSTURMA, GANTT, NRDECORES, LOGGANTT, COMPMINCONJ, IDGRUPOMAQUINA,
                PRODUTIVIDADEPADRAO, EFICIENCIAPADRAO, TAREFAATUAL, INICIOTAREFAATUAL,
                FIMPREVTAREFAATUAL, PARADAATUAL, INICIOPARADAATUAL, FIMPREVPARADAATUAL,
                IDSECAOMAQUINAPARADAATUAL, PROGRAMARPRODUCAO, DESATIVADA, CODIGOERP, PERDALIMITEAVISO,
                UNIDADEAPONTCONJUGACAO, TESTEPORBOLETIM, IDJORNADA, DISTMINVINCOS, IDCENTROCUSTO,
                IDCENTROCUSTOMAQ, IDSESSAODB, PORCMINLARGURARESINADA, CARGAMAQLOTE,
                VALIDAINTERSECCAOAPONTAMENTO, DESCVALIDAINTERSECCAOAPONT, VALIDABURACOAPONTAMENTO,
                DESCVALIDABURACOAPONTAMENTO, CONSEGUIREFILARSOMENTEUMLADO, IDUNIDADEFABRIL,
                REFILEDIRETOPRENSA, AREAM2PERDIDAPORCONJUGACAO, AREAM2PERDIDOTROCAFORMATO,
                DIFPORCPRODUTMAQFT_MENOS, DIFPORCPRODUTMAQFT_MAIS, PEDIDOMINIMOM2, PEDIDOMINIMOKG,
                LIMITAMINIMOACESSORIO, DISPONIVELLOTENOVO, PERDAPRODUCAOPERC, PERDAPRODUCAOPECAS,
                DESLOCMAXIMPORTABOBINAS_MM, LARGURALIMITEESTABILIDADEPILHA, COMPRIMENTOREFOGOGUILHOTINA,
                HABILITARINTEGRACAOESTEIRAOND
            ) VALUES (
                :MAQ_ID, :MAQUINA, :NOMEMAQUINA, :TIPO, :FACOES, :LARGUTILMAX, :LARGMINCHAPA,
                :LARGMAXCHAPA, :COMPMINCHAPA, :COMPMAXCHAPA, :REFILOMIN, :REFILOMAX, :FACAS,
                :PERMITEMISTURARFERRAMENTAS, :IDTIPOVINCOPADRAO, :TEARTAPE, :RESINAINTERNA, :RESINAEXTERNA,
                :ENDURECEDORMIOLO, :ROTACAOMAXIMA, :CUSTOHORA, :CUSTOMETRO, :CUSTOMETROQUAD, :FORMATOPADRAO,
                :UNIDPRODUTIVIDADE, :DESCUNIDPRODUTIVIDADE, :SETUP, :PRODM2, :PRODBATIDAS, :PRODKG,
                :PRODMAQUINA, :HOMENSTURMA, :GANTT, :NRDECORES, :LOGGANTT, :COMPMINCONJ, :IDGRUPOMAQUINA,
                :PRODUTIVIDADEPADRAO, :EFICIENCIAPADRAO, :TAREFAATUAL, :INICIOTAREFAATUAL,
                :FIMPREVTAREFAATUAL, :PARADAATUAL, :INICIOPARADAATUAL, :FIMPREVPARADAATUAL,
                :IDSECAOMAQUINAPARADAATUAL, :PROGRAMARPRODUCAO, :DESATIVADA, :CODIGOERP, :PERDALIMITEAVISO,
                :UNIDADEAPONTCONJUGACAO, :TESTEPORBOLETIM, :IDJORNADA, :DISTMINVINCOS, :IDCENTROCUSTO,
                :IDCENTROCUSTOMAQ, :IDSESSAODB, :PORCMINLARGURARESINADA, :CARGAMAQLOTE,
                :VALIDAINTERSECCAOAPONTAMENTO, :DESCVALIDAINTERSECCAOAPONT, :VALIDABURACOAPONTAMENTO,
                :DESCVALIDABURACOAPONTAMENTO, :CONSEGUIREFILARSOMENTEUMLADO, :IDUNIDADEFABRIL,
                :REFILEDIRETOPRENSA, :AREAM2PERDIDAPORCONJUGACAO, :AREAM2PERDIDOTROCAFORMATO,
                :DIFPORCPRODUTMAQFT_MENOS, :DIFPORCPRODUTMAQFT_MAIS, :PEDIDOMINIMOM2, :PEDIDOMINIMOKG,
                :LIMITAMINIMOACESSORIO, :DISPONIVELLOTENOVO, :PERDAPRODUCAOPERC, :PERDAPRODUCAOPECAS,
                :DESLOCMAXIMPORTABOBINAS_MM, :LARGURALIMITEESTABILIDADEPILHA, :COMPRIMENTOREFOGOGUILHOTINA,
                :HABILITARINTEGRACAOESTEIRAOND
            )
        """
        
        # Configurar inputs específicos para TIMESTAMP
        for param in payload:
            for date_field in ['INICIOTAREFAATUAL', 'FIMPREVTAREFAATUAL', 'INICIOPARADAATUAL', 'FIMPREVPARADAATUAL']:
                if date_field in param and isinstance(param[date_field], datetime):
                    if param[date_field].microsecond == 0:
                        param[date_field] = param[date_field].replace(microsecond=123456)
        
        # Executa o INSERT
        cur.executemany(insert_sql, payload)
        dst.commit()
        
        # Verifica quantas linhas foram inseridas
        cur.execute("SELECT COUNT(*) FROM MAQUINA")
        count_result = cur.fetchone()
        total_inserido = count_result[0]
        
        log.info("Oracle <- %s registros inseridos com sucesso na tabela MAQUINA. Total na tabela: %s", 
                len(payload), total_inserido)
            
    except Exception as e:
        log.error("Erro ao fazer TRUNCATE + INSERT no Oracle: %s", str(e))
        dst.rollback()
        raise
    finally:
        dst.close()

# -----------------
# DAG para MAQUINA
# -----------------
with DAG(
    dag_id="etl_maquina",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "sqlserver", "oracle", "maquina"],
):
    truncate_insert = PythonOperator(
        task_id="truncate_insert_maquina",
        python_callable=etl_maquina,
    )