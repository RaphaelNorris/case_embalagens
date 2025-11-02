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
        if nan_date == "401404":
            return datetime(2999, 12, 31)
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
            if nan_date == "401404":
                return datetime(2999, 12, 31)
            return None
    
    try:
        return datetime.combine(value, datetime.min.time())
    except Exception:
        if nan_date == "401404":
            return datetime(2999, 12, 31)
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

def _map_row_to_refined_pedidos(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeamento da TRUSTED para REFINED com conversões de tipo e tratamento de NaN.
    """
    # DEBUG: Log para verificar a estrutura dos dados
    if not hasattr(_map_row_to_refined_pedidos, 'logged_structure'):
        log.info("Estrutura da linha recebida da TRUSTED: %s", list(row.keys())[:10])
        _map_row_to_refined_pedidos.logged_structure = True
    
    return {
        "CD_ESPELHO": _convert_to_varchar(row.get("ESPELHO"), "-1", "CD_ESPELHO"),
        "CD_FACA": _convert_to_varchar(row.get("FACA"), "-1", "CD_FACA"),
        "CD_FILME": _convert_to_varchar(row.get("FILME"), "-1", "CD_FILME"),
        "CD_LAPINTERNO": _convert_to_varchar(row.get("LAPINTERNO"), "-1", "CD_LAPINTERNO"),
        "CD_LAPNOCOMP": _convert_to_varchar(row.get("LAPNOCOMP"), "-1", "CD_LAPNOCOMP"),
        "CD_REFERENCIA": _convert_to_varchar(row.get("CODIGOREFERENCIA"), "-1", "CD_REFERENCIA"),
        "DT_ENTREGA2": _convert_to_timestamp(row.get("DATAENTREGA2"), "401404"),
        "DT_ENTREGAORIGINAL": _convert_to_timestamp(row.get("DATAENTREGAORIGINAL"), "401404"),
        "FL_AMARRADO": _convert_to_varchar(_handle_nan(row.get("AMARRADO"), 0), "0", "FL_AMARRADO"),
        "FL_CHAPA": _convert_to_varchar(_handle_nan(row.get("CHAPA"), 0), "0", "FL_CHAPA"),
        "TX_COR3": _convert_to_varchar(row.get("COR3"), "", "TX_COR3"),
        "TX_COR4": _convert_to_varchar(row.get("COR4"), "", "TX_COR4"),
        "FL_EXIGELAUDO": _convert_to_varchar(_handle_nan(row.get("EXIGELAUDO"), 0), "0", "FL_EXIGELAUDO"),
        "FL_PALETIZADO": _convert_to_varchar(_handle_nan(row.get("PALETIZADO"), 0), "0", "FL_PALETIZADO"),
        "FL_REFILADO": _convert_to_varchar(_handle_nan(row.get("REFILADO"), 0), "0", "FL_REFILADO"),
        "FL_RESINAINTERNA": _convert_to_varchar(_handle_nan(row.get("RESINAINTERNA"), 0), "0", "FL_RESINAINTERNA"),
        "FL_SUSPENSO": _convert_to_varchar(_handle_nan(row.get("SUSPENSO"), 0), "0", "FL_SUSPENSO"),
        "TX_SUSPOUCANCEL": _convert_to_varchar(row.get("SUSPOUCANCEL"), "", "TX_SUSPOUCANCEL"),
        "FL_TIPOENTREGA": _convert_to_varchar(_handle_nan(row.get("TIPOENTREGA"), 0), "0", "FL_TIPOENTREGA"),
        "ID_CLIENTE": _convert_to_varchar(row.get("IDCLIENTE"), "-1", "ID_CLIENTE"),
        "ID_ITEM": _convert_to_varchar(row.get("ITEM"), "-1", "ID_ITEM"),
        "ID_PALETE": _convert_to_varchar(row.get("IDPALETE"), "-1", "ID_PALETE"),
        "ID_PEDIDO": _convert_to_varchar(row.get("IDPEDIDOS"), "-1", "ID_PEDIDO"),
        "ID_TIPOFT2": _convert_to_varchar(row.get("IDTIPOFT2"), "-1", "ID_TIPOFT2"),
        "QT_ARRANJO": _convert_to_number(row.get("ARRANJO"), 0),
        "QT_COBBINTMAXIMO": _convert_to_number(row.get("COBBINTMAXIMO"), 0),
        "QT_LAP": _convert_to_number(row.get("LAP"), 0),
        "QT_NRCORES": _convert_to_number(row.get("NRCORES"), 0),
        "QT_PACOTESPORPALETE": _convert_to_number(row.get("PACOTESPORPALETE"), 0),
        "QT_PECASPORPACOTE": _convert_to_number(row.get("PECASPORPACOTE"), 0),
        "QT_PECASPORPALETE": _convert_to_number(row.get("PECASPORPALETE"), 0),
        "QT_PEDIDA": _convert_to_number(row.get("QUANTIDADEPEDIDA"), 0),
        "QT_PEDIDAMAX": _convert_to_number(row.get("QUANTIDADEPEDIDAMAX"), 0),
        "QT_PEDIDAMIN": _convert_to_number(row.get("QUANTIDADEPEDIDAMIN"), 0),
        "QT_PROLONGLAP": _convert_to_number(row.get("PROLONGLAP"), 0),
        "QT_UNIDADESPORPALETE": _convert_to_number(row.get("UNIDADESPORPALETE"), 0),
        "ST_PEDIDO": _convert_to_varchar(row.get("STATUSPEDIDO"), " ", "ST_PEDIDO"),
        "TX_COMPOSICAO": _convert_to_varchar(row.get("COMPOSICAO"), "", "TX_COMPOSICAO"),
        "TX_COR1": _convert_to_varchar(row.get("COR1"), "", "TX_COR1"),
        "TX_COR2": _convert_to_varchar(row.get("COR2"), "", "TX_COR2"),
        "TX_DESCRSTATUSPEDIDO": _convert_to_varchar(row.get("DESCRSTATUSPEDIDO"), "", "TX_DESCRSTATUSPEDIDO"),
        "TX_DESCRTIPODOPEDIDO": _convert_to_varchar(row.get("DESCRTIPODOPEDIDO"), "", "TX_DESCRTIPODOPEDIDO"),
        "TX_DESCTIPOENTREGA": _convert_to_varchar(row.get("DESCTIPOENTREGA"), "", "TX_DESCTIPOENTREGA"),
        "TX_PATHFIGURADOLASTRO": _convert_to_varchar(row.get("PATHFIGURADOLASTRO"), "", "TX_PATHFIGURADOLASTRO"),
        "TX_REFERENCIA": _convert_to_varchar(row.get("REFERENCIA"), "", "TX_REFERENCIA"),
        "TX_TIPOABNT": _convert_to_varchar(row.get("TIPOABNT"), "", "TX_TIPOABNT"),
        "VL_ALTURAINTERNA": _convert_to_number(row.get("ALTURAINTERNA"), 0),
        "VL_ALTURAPACOTE": _convert_to_number(row.get("ALTURAPACOTE"), 0),
        "VL_ALTURAPALETEFECHADO": _convert_to_number(row.get("ALTURAPALETEFECHADO"), 0),
        "VL_AREABRUTACHAPA": _convert_to_number(row.get("AREABRUTACHAPA"), 0),
        "VL_AREABRUTAPECA": _convert_to_number(row.get("AREABRUTAPECA"), 0),
        "VL_AREABRUTAPECACOMREFILOS": _convert_to_number(row.get("AREABRUTAPECACOMREFILOS"), 0),
        "VL_AREALIQUIDACHAPA": _convert_to_number(row.get("AREALIQUIDACHAPA"), 0),
        "VL_AREALIQUIDAPECA": _convert_to_number(row.get("AREALIQUIDAPECA"), 0),
        "VL_COLUNAMINIMO": _convert_to_number(row.get("COLUNAMINIMO"), 0),
        "VL_COMPPACOTE": _convert_to_number(row.get("COMPPACOTE"), 0),
        "VL_COMPPALETEFECHADO": _convert_to_number(row.get("COMPPALETEFECHADO"), 0),
        "VL_COMPPECA": _convert_to_number(row.get("COMPPECA"), 0),
        "VL_COMPRESSAO": _convert_to_number(row.get("COMPRESSAO"), 0),
        "VL_COMPRIMENTO": _convert_to_number(row.get("COMPRIMENTO"), 0),
        "VL_COMPRIMENTOINTERNO": _convert_to_number(row.get("COMPRIMENTOINTERNO"), 0),
        "VL_CONSUMOCOR1": _convert_to_number(row.get("CONSUMOCOR1"), 0),
        "VL_CONSUMOCOR2": _convert_to_number(row.get("CONSUMOCOR2"), 0),
        "VL_CONSUMOCOR3": _convert_to_number(row.get("CONSUMOCOR3"), 0),
        "VL_CONSUMOCOR4": _convert_to_number(row.get("CONSUMOCOR4"), 0),
        "VL_GRAMATURA": _convert_to_number(row.get("GRAMATURA"), 0),
        "VL_LARGPACOTE": _convert_to_number(row.get("LARGPACOTE"), 0),
        "VL_LARGPALETEFECHADO": _convert_to_number(row.get("LARGPALETEFECHADO"), 0),
        "VL_LARGPECA": _convert_to_number(row.get("LARGPECA"), 0),
        "VL_LARGURA": _convert_to_number(row.get("LARGURA"), 0),
        "VL_LARGURAINTERNA": _convert_to_number(row.get("LARGURAINTERNA"), 0),
        "VL_MULTCOMP": _convert_to_number(row.get("MULTCOMP"), 0),
        "VL_MULTLARG": _convert_to_number(row.get("MULTLARG"), 0),
        "VL_PACOTESALTURA": _convert_to_number(row.get("PACOTESALTURA"), 0),
        "VL_PACOTESCOMPRIMENTO": _convert_to_number(row.get("PACOTESCOMPRIMENTO"), 0),
        "VL_PACOTESLARGURA": _convert_to_number(row.get("PACOTESLARGURA"), 0),
        "VL_PESOCAIXA": _convert_to_number(row.get("PESOCAIXA"), 0),
        "VL_PESOPECA": _convert_to_number(row.get("PESOPECA"), 0),
        "VL_REFILOCOMPRIMENTO": _convert_to_number(row.get("REFILOCOMPRIMENTO"), 0),
        "VL_REFILOLARGURA": _convert_to_number(row.get("REFILOLARGURA"), 0),
        "VL_REFUGOCLIENTE": _convert_to_number(row.get("REFUGOCLIENTE"), 0),
        "VL_VINCOCOMP1": _convert_to_number(row.get("VINCOCOMP1"), 0),
        "VL_VINCOCOMP2": _convert_to_number(row.get("VINCOCOMP2"), 0),
        "VL_VINCOCOMP3": _convert_to_number(row.get("VINCOCOMP3"), 0),
        "VL_VINCOCOMP4": _convert_to_number(row.get("VINCOCOMP4"), 0),
        "VL_VINCOCOMP5": _convert_to_number(row.get("VINCOCOMP5"), 0),
        "VL_VINCOLARG1": _convert_to_number(row.get("VINCOLARG1"), 0),
        "VL_VINCOLARG2": _convert_to_number(row.get("VINCOLARG2"), 0),
        "VL_VINCOLARG3": _convert_to_number(row.get("VINCOLARG3"), 0),
        "VL_VOLUMEFECHADOPEDIDO": _convert_to_number(row.get("VOLUMEFECHADOPEDIDO"), 0),
        "VL_VOLUMEPACOTEFECHADOM3": _convert_to_number(row.get("VOLUMEPACOTEFECHADOM3"), 0),
        "VL_VOLUMEPALETEFECHADOM3": _convert_to_number(row.get("VOLUMEPALETEFECHADOM3"), 0),
    }

# -----------------
# Tarefa principal
# -----------------
def etl_pedidos_trusted_to_refined(**context):
    # Configuração de paginação - 40.000 registros por lote
    page_size = 40000
    offset = 0
    total_processed = 0
    batch_count = 0
    
    # **ALTERAÇÃO: REMOVIDA a limpeza da tabela destino**
    log.info("Iniciando ETL TRUSTED -> REFINED sem limpar tabela destino")
    
    # Loop de paginação
    while True:
        # Query com paginação da tabela TRUSTED
        sql = """
            SELECT * FROM PEDIDOS 
            ORDER BY IDPEDIDOS, ITEM
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
            
            log.info("TRUSTED -> Página %s: %s registros extraídos da tabela PEDIDOS.", 
                    batch_count + 1, len(rows))

            if not rows:
                log.info("Todas as páginas processadas. Total: %s registros.", total_processed)
                break

            # 2) Mapeia para o layout do REFINED
            payload = []
            mapping_errors = 0
            
            for r in rows:
                try:
                    mapped_row = _map_row_to_refined_pedidos(r)
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
                _process_batch_pedidos_refined(payload, batch_count + 1)
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

def _process_batch_pedidos_refined(payload, batch_number):
    """Processa um lote de registros no Oracle REFINED com MERGE (UPSERT)"""
    
    # **CORREÇÃO: Substituído INSERT por MERGE para evitar duplicação**
    merge_sql = """
        MERGE INTO PEDIDOS t 
        USING (SELECT 
            :CD_ESPELHO as CD_ESPELHO,
            :CD_FACA as CD_FACA,
            :CD_FILME as CD_FILME,
            :CD_LAPINTERNO as CD_LAPINTERNO,
            :CD_LAPNOCOMP as CD_LAPNOCOMP,
            :CD_REFERENCIA as CD_REFERENCIA,
            :DT_ENTREGA2 as DT_ENTREGA2,
            :DT_ENTREGAORIGINAL as DT_ENTREGAORIGINAL,
            :FL_AMARRADO as FL_AMARRADO,
            :FL_CHAPA as FL_CHAPA,
            :TX_COR3 as TX_COR3,
            :TX_COR4 as TX_COR4,
            :FL_EXIGELAUDO as FL_EXIGELAUDO,
            :FL_PALETIZADO as FL_PALETIZADO,
            :FL_REFILADO as FL_REFILADO,
            :FL_RESINAINTERNA as FL_RESINAINTERNA,
            :FL_SUSPENSO as FL_SUSPENSO,
            :TX_SUSPOUCANCEL as TX_SUSPOUCANCEL,
            :FL_TIPOENTREGA as FL_TIPOENTREGA,
            :ID_CLIENTE as ID_CLIENTE,
            :ID_ITEM as ID_ITEM,
            :ID_PALETE as ID_PALETE,
            :ID_PEDIDO as ID_PEDIDO,
            :ID_TIPOFT2 as ID_TIPOFT2,
            :QT_ARRANJO as QT_ARRANJO,
            :QT_COBBINTMAXIMO as QT_COBBINTMAXIMO,
            :QT_LAP as QT_LAP,
            :QT_NRCORES as QT_NRCORES,
            :QT_PACOTESPORPALETE as QT_PACOTESPORPALETE,
            :QT_PECASPORPACOTE as QT_PECASPORPACOTE,
            :QT_PECASPORPALETE as QT_PECASPORPALETE,
            :QT_PEDIDA as QT_PEDIDA,
            :QT_PEDIDAMAX as QT_PEDIDAMAX,
            :QT_PEDIDAMIN as QT_PEDIDAMIN,
            :QT_PROLONGLAP as QT_PROLONGLAP,
            :QT_UNIDADESPORPALETE as QT_UNIDADESPORPALETE,
            :ST_PEDIDO as ST_PEDIDO,
            :TX_COMPOSICAO as TX_COMPOSICAO,
            :TX_COR1 as TX_COR1,
            :TX_COR2 as TX_COR2,
            :TX_DESCRSTATUSPEDIDO as TX_DESCRSTATUSPEDIDO,
            :TX_DESCRTIPODOPEDIDO as TX_DESCRTIPODOPEDIDO,
            :TX_DESCTIPOENTREGA as TX_DESCTIPOENTREGA,
            :TX_PATHFIGURADOLASTRO as TX_PATHFIGURADOLASTRO,
            :TX_REFERENCIA as TX_REFERENCIA,
            :TX_TIPOABNT as TX_TIPOABNT,
            :VL_ALTURAINTERNA as VL_ALTURAINTERNA,
            :VL_ALTURAPACOTE as VL_ALTURAPACOTE,
            :VL_ALTURAPALETEFECHADO as VL_ALTURAPALETEFECHADO,
            :VL_AREABRUTACHAPA as VL_AREABRUTACHAPA,
            :VL_AREABRUTAPECA as VL_AREABRUTAPECA,
            :VL_AREABRUTAPECACOMREFILOS as VL_AREABRUTAPECACOMREFILOS,
            :VL_AREALIQUIDACHAPA as VL_AREALIQUIDACHAPA,
            :VL_AREALIQUIDAPECA as VL_AREALIQUIDAPECA,
            :VL_COLUNAMINIMO as VL_COLUNAMINIMO,
            :VL_COMPPACOTE as VL_COMPPACOTE,
            :VL_COMPPALETEFECHADO as VL_COMPPALETEFECHADO,
            :VL_COMPPECA as VL_COMPPECA,
            :VL_COMPRESSAO as VL_COMPRESSAO,
            :VL_COMPRIMENTO as VL_COMPRIMENTO,
            :VL_COMPRIMENTOINTERNO as VL_COMPRIMENTOINTERNO,
            :VL_CONSUMOCOR1 as VL_CONSUMOCOR1,
            :VL_CONSUMOCOR2 as VL_CONSUMOCOR2,
            :VL_CONSUMOCOR3 as VL_CONSUMOCOR3,
            :VL_CONSUMOCOR4 as VL_CONSUMOCOR4,
            :VL_GRAMATURA as VL_GRAMATURA,
            :VL_LARGPACOTE as VL_LARGPACOTE,
            :VL_LARGPALETEFECHADO as VL_LARGPALETEFECHADO,
            :VL_LARGPECA as VL_LARGPECA,
            :VL_LARGURA as VL_LARGURA,
            :VL_LARGURAINTERNA as VL_LARGURAINTERNA,
            :VL_MULTCOMP as VL_MULTCOMP,
            :VL_MULTLARG as VL_MULTLARG,
            :VL_PACOTESALTURA as VL_PACOTESALTURA,
            :VL_PACOTESCOMPRIMENTO as VL_PACOTESCOMPRIMENTO,
            :VL_PACOTESLARGURA as VL_PACOTESLARGURA,
            :VL_PESOCAIXA as VL_PESOCAIXA,
            :VL_PESOPECA as VL_PESOPECA,
            :VL_REFILOCOMPRIMENTO as VL_REFILOCOMPRIMENTO,
            :VL_REFILOLARGURA as VL_REFILOLARGURA,
            :VL_REFUGOCLIENTE as VL_REFUGOCLIENTE,
            :VL_VINCOCOMP1 as VL_VINCOCOMP1,
            :VL_VINCOCOMP2 as VL_VINCOCOMP2,
            :VL_VINCOCOMP3 as VL_VINCOCOMP3,
            :VL_VINCOCOMP4 as VL_VINCOCOMP4,
            :VL_VINCOCOMP5 as VL_VINCOCOMP5,
            :VL_VINCOLARG1 as VL_VINCOLARG1,
            :VL_VINCOLARG2 as VL_VINCOLARG2,
            :VL_VINCOLARG3 as VL_VINCOLARG3,
            :VL_VOLUMEFECHADOPEDIDO as VL_VOLUMEFECHADOPEDIDO,
            :VL_VOLUMEPACOTEFECHADOM3 as VL_VOLUMEPACOTEFECHADOM3,
            :VL_VOLUMEPALETEFECHADOM3 as VL_VOLUMEPALETEFECHADOM3
        FROM dual) s 
        ON (t.ID_PEDIDO = s.ID_PEDIDO AND t.ID_ITEM = s.ID_ITEM)
        WHEN MATCHED THEN UPDATE SET 
            t.CD_ESPELHO = s.CD_ESPELHO,
            t.CD_FACA = s.CD_FACA,
            t.CD_FILME = s.CD_FILME,
            t.CD_LAPINTERNO = s.CD_LAPINTERNO,
            t.CD_LAPNOCOMP = s.CD_LAPNOCOMP,
            t.CD_REFERENCIA = s.CD_REFERENCIA,
            t.DT_ENTREGA2 = s.DT_ENTREGA2,
            t.DT_ENTREGAORIGINAL = s.DT_ENTREGAORIGINAL,
            t.FL_AMARRADO = s.FL_AMARRADO,
            t.FL_CHAPA = s.FL_CHAPA,
            t.TX_COR3 = s.TX_COR3,
            t.TX_COR4 = s.TX_COR4,
            t.FL_EXIGELAUDO = s.FL_EXIGELAUDO,
            t.FL_PALETIZADO = s.FL_PALETIZADO,
            t.FL_REFILADO = s.FL_REFILADO,
            t.FL_RESINAINTERNA = s.FL_RESINAINTERNA,
            t.FL_SUSPENSO = s.FL_SUSPENSO,
            t.TX_SUSPOUCANCEL = s.TX_SUSPOUCANCEL,
            t.FL_TIPOENTREGA = s.FL_TIPOENTREGA,
            t.ID_CLIENTE = s.ID_CLIENTE,
            t.ID_PALETE = s.ID_PALETE,
            t.ID_TIPOFT2 = s.ID_TIPOFT2,
            t.QT_ARRANJO = s.QT_ARRANJO,
            t.QT_COBBINTMAXIMO = s.QT_COBBINTMAXIMO,
            t.QT_LAP = s.QT_LAP,
            t.QT_NRCORES = s.QT_NRCORES,
            t.QT_PACOTESPORPALETE = s.QT_PACOTESPORPALETE,
            t.QT_PECASPORPACOTE = s.QT_PECASPORPACOTE,
            t.QT_PECASPORPALETE = s.QT_PECASPORPALETE,
            t.QT_PEDIDA = s.QT_PEDIDA,
            t.QT_PEDIDAMAX = s.QT_PEDIDAMAX,
            t.QT_PEDIDAMIN = s.QT_PEDIDAMIN,
            t.QT_PROLONGLAP = s.QT_PROLONGLAP,
            t.QT_UNIDADESPORPALETE = s.QT_UNIDADESPORPALETE,
            t.ST_PEDIDO = s.ST_PEDIDO,
            t.TX_COMPOSICAO = s.TX_COMPOSICAO,
            t.TX_COR1 = s.TX_COR1,
            t.TX_COR2 = s.TX_COR2,
            t.TX_DESCRSTATUSPEDIDO = s.TX_DESCRSTATUSPEDIDO,
            t.TX_DESCRTIPODOPEDIDO = s.TX_DESCRTIPODOPEDIDO,
            t.TX_DESCTIPOENTREGA = s.TX_DESCTIPOENTREGA,
            t.TX_PATHFIGURADOLASTRO = s.TX_PATHFIGURADOLASTRO,
            t.TX_REFERENCIA = s.TX_REFERENCIA,
            t.TX_TIPOABNT = s.TX_TIPOABNT,
            t.VL_ALTURAINTERNA = s.VL_ALTURAINTERNA,
            t.VL_ALTURAPACOTE = s.VL_ALTURAPACOTE,
            t.VL_ALTURAPALETEFECHADO = s.VL_ALTURAPALETEFECHADO,
            t.VL_AREABRUTACHAPA = s.VL_AREABRUTACHAPA,
            t.VL_AREABRUTAPECA = s.VL_AREABRUTAPECA,
            t.VL_AREABRUTAPECACOMREFILOS = s.VL_AREABRUTAPECACOMREFILOS,
            t.VL_AREALIQUIDACHAPA = s.VL_AREALIQUIDACHAPA,
            t.VL_AREALIQUIDAPECA = s.VL_AREALIQUIDAPECA,
            t.VL_COLUNAMINIMO = s.VL_COLUNAMINIMO,
            t.VL_COMPPACOTE = s.VL_COMPPACOTE,
            t.VL_COMPPALETEFECHADO = s.VL_COMPPALETEFECHADO,
            t.VL_COMPPECA = s.VL_COMPPECA,
            t.VL_COMPRESSAO = s.VL_COMPRESSAO,
            t.VL_COMPRIMENTO = s.VL_COMPRIMENTO,
            t.VL_COMPRIMENTOINTERNO = s.VL_COMPRIMENTOINTERNO,
            t.VL_CONSUMOCOR1 = s.VL_CONSUMOCOR1,
            t.VL_CONSUMOCOR2 = s.VL_CONSUMOCOR2,
            t.VL_CONSUMOCOR3 = s.VL_CONSUMOCOR3,
            t.VL_CONSUMOCOR4 = s.VL_CONSUMOCOR4,
            t.VL_GRAMATURA = s.VL_GRAMATURA,
            t.VL_LARGPACOTE = s.VL_LARGPACOTE,
            t.VL_LARGPALETEFECHADO = s.VL_LARGPALETEFECHADO,
            t.VL_LARGPECA = s.VL_LARGPECA,
            t.VL_LARGURA = s.VL_LARGURA,
            t.VL_LARGURAINTERNA = s.VL_LARGURAINTERNA,
            t.VL_MULTCOMP = s.VL_MULTCOMP,
            t.VL_MULTLARG = s.VL_MULTLARG,
            t.VL_PACOTESALTURA = s.VL_PACOTESALTURA,
            t.VL_PACOTESCOMPRIMENTO = s.VL_PACOTESCOMPRIMENTO,
            t.VL_PACOTESLARGURA = s.VL_PACOTESLARGURA,
            t.VL_PESOCAIXA = s.VL_PESOCAIXA,
            t.VL_PESOPECA = s.VL_PESOPECA,
            t.VL_REFILOCOMPRIMENTO = s.VL_REFILOCOMPRIMENTO,
            t.VL_REFILOLARGURA = s.VL_REFILOLARGURA,
            t.VL_REFUGOCLIENTE = s.VL_REFUGOCLIENTE,
            t.VL_VINCOCOMP1 = s.VL_VINCOCOMP1,
            t.VL_VINCOCOMP2 = s.VL_VINCOCOMP2,
            t.VL_VINCOCOMP3 = s.VL_VINCOCOMP3,
            t.VL_VINCOCOMP4 = s.VL_VINCOCOMP4,
            t.VL_VINCOCOMP5 = s.VL_VINCOCOMP5,
            t.VL_VINCOLARG1 = s.VL_VINCOLARG1,
            t.VL_VINCOLARG2 = s.VL_VINCOLARG2,
            t.VL_VINCOLARG3 = s.VL_VINCOLARG3,
            t.VL_VOLUMEFECHADOPEDIDO = s.VL_VOLUMEFECHADOPEDIDO,
            t.VL_VOLUMEPACOTEFECHADOM3 = s.VL_VOLUMEPACOTEFECHADOM3,
            t.VL_VOLUMEPALETEFECHADOM3 = s.VL_VOLUMEPALETEFECHADOM3
        WHEN NOT MATCHED THEN INSERT (
            CD_ESPELHO, CD_FACA, CD_FILME, CD_LAPINTERNO, CD_LAPNOCOMP, CD_REFERENCIA,
            DT_ENTREGA2, DT_ENTREGAORIGINAL, FL_AMARRADO, FL_CHAPA, TX_COR3, TX_COR4,
            FL_EXIGELAUDO, FL_PALETIZADO, FL_REFILADO, FL_RESINAINTERNA, FL_SUSPENSO,
            TX_SUSPOUCANCEL, FL_TIPOENTREGA, ID_CLIENTE, ID_ITEM, ID_PALETE, ID_PEDIDO,
            ID_TIPOFT2, QT_ARRANJO, QT_COBBINTMAXIMO, QT_LAP, QT_NRCORES, QT_PACOTESPORPALETE,
            QT_PECASPORPACOTE, QT_PECASPORPALETE, QT_PEDIDA, QT_PEDIDAMAX, QT_PEDIDAMIN,
            QT_PROLONGLAP, QT_UNIDADESPORPALETE, ST_PEDIDO, TX_COMPOSICAO, TX_COR1, TX_COR2,
            TX_DESCRSTATUSPEDIDO, TX_DESCRTIPODOPEDIDO, TX_DESCTIPOENTREGA, TX_PATHFIGURADOLASTRO,
            TX_REFERENCIA, TX_TIPOABNT, VL_ALTURAINTERNA, VL_ALTURAPACOTE, VL_ALTURAPALETEFECHADO,
            VL_AREABRUTACHAPA, VL_AREABRUTAPECA, VL_AREABRUTAPECACOMREFILOS, VL_AREALIQUIDACHAPA,
            VL_AREALIQUIDAPECA, VL_COLUNAMINIMO, VL_COMPPACOTE, VL_COMPPALETEFECHADO, VL_COMPPECA,
            VL_COMPRESSAO, VL_COMPRIMENTO, VL_COMPRIMENTOINTERNO, VL_CONSUMOCOR1, VL_CONSUMOCOR2,
            VL_CONSUMOCOR3, VL_CONSUMOCOR4, VL_GRAMATURA, VL_LARGPACOTE, VL_LARGPALETEFECHADO,
            VL_LARGPECA, VL_LARGURA, VL_LARGURAINTERNA, VL_MULTCOMP, VL_MULTLARG, VL_PACOTESALTURA,
            VL_PACOTESCOMPRIMENTO, VL_PACOTESLARGURA, VL_PESOCAIXA, VL_PESOPECA, VL_REFILOCOMPRIMENTO,
            VL_REFILOLARGURA, VL_REFUGOCLIENTE, VL_VINCOCOMP1, VL_VINCOCOMP2, VL_VINCOCOMP3,
            VL_VINCOCOMP4, VL_VINCOCOMP5, VL_VINCOLARG1, VL_VINCOLARG2, VL_VINCOLARG3,
            VL_VOLUMEFECHADOPEDIDO, VL_VOLUMEPACOTEFECHADOM3, VL_VOLUMEPALETEFECHADOM3
        ) VALUES (
            s.CD_ESPELHO, s.CD_FACA, s.CD_FILME, s.CD_LAPINTERNO, s.CD_LAPNOCOMP, s.CD_REFERENCIA,
            s.DT_ENTREGA2, s.DT_ENTREGAORIGINAL, s.FL_AMARRADO, s.FL_CHAPA, s.TX_COR3, s.TX_COR4,
            s.FL_EXIGELAUDO, s.FL_PALETIZADO, s.FL_REFILADO, s.FL_RESINAINTERNA, s.FL_SUSPENSO,
            s.TX_SUSPOUCANCEL, s.FL_TIPOENTREGA, s.ID_CLIENTE, s.ID_ITEM, s.ID_PALETE, s.ID_PEDIDO,
            s.ID_TIPOFT2, s.QT_ARRANJO, s.QT_COBBINTMAXIMO, s.QT_LAP, s.QT_NRCORES, s.QT_PACOTESPORPALETE,
            s.QT_PECASPORPACOTE, s.QT_PECASPORPALETE, s.QT_PEDIDA, s.QT_PEDIDAMAX, s.QT_PEDIDAMIN,
            s.QT_PROLONGLAP, s.QT_UNIDADESPORPALETE, s.ST_PEDIDO, s.TX_COMPOSICAO, s.TX_COR1, s.TX_COR2,
            s.TX_DESCRSTATUSPEDIDO, s.TX_DESCRTIPODOPEDIDO, s.TX_DESCTIPOENTREGA, s.TX_PATHFIGURADOLASTRO,
            s.TX_REFERENCIA, s.TX_TIPOABNT, s.VL_ALTURAINTERNA, s.VL_ALTURAPACOTE, s.VL_ALTURAPALETEFECHADO,
            s.VL_AREABRUTACHAPA, s.VL_AREABRUTAPECA, s.VL_AREABRUTAPECACOMREFILOS, s.VL_AREALIQUIDACHAPA,
            s.VL_AREALIQUIDAPECA, s.VL_COLUNAMINIMO, s.VL_COMPPACOTE, s.VL_COMPPALETEFECHADO, s.VL_COMPPECA,
            s.VL_COMPRESSAO, s.VL_COMPRIMENTO, s.VL_COMPRIMENTOINTERNO, s.VL_CONSUMOCOR1, s.VL_CONSUMOCOR2,
            s.VL_CONSUMOCOR3, s.VL_CONSUMOCOR4, s.VL_GRAMATURA, s.VL_LARGPACOTE, s.VL_LARGPALETEFECHADO,
            s.VL_LARGPECA, s.VL_LARGURA, s.VL_LARGURAINTERNA, s.VL_MULTCOMP, s.VL_MULTLARG, s.VL_PACOTESALTURA,
            s.VL_PACOTESCOMPRIMENTO, s.VL_PACOTESLARGURA, s.VL_PESOCAIXA, s.VL_PESOPECA, s.VL_REFILOCOMPRIMENTO,
            s.VL_REFILOLARGURA, s.VL_REFUGOCLIENTE, s.VL_VINCOCOMP1, s.VL_VINCOCOMP2, s.VL_VINCOCOMP3,
            s.VL_VINCOCOMP4, s.VL_VINCOCOMP5, s.VL_VINCOLARG1, s.VL_VINCOLARG2, s.VL_VINCOLARG3,
            s.VL_VOLUMEFECHADOPEDIDO, s.VL_VOLUMEPACOTEFECHADOM3, s.VL_VOLUMEPALETEFECHADOM3
        )
    """

    dst = _make_oracle_conn_refined()
    try:
        cur = dst.cursor()
        
        # Executa o MERGE
        cur.executemany(merge_sql, payload)
        dst.commit()
        log.info("REFINED <- Lote %s: %s registros processados com MERGE (UPSERT).", batch_number, len(payload))
            
    except Exception as e:
        log.error("Erro ao fazer MERGE no Oracle REFINED (lote %s): %s", batch_number, str(e))
        dst.rollback()
        raise
    finally:
        dst.close()

# -----------------
# DAG
# -----------------
with DAG(
    dag_id="etl_trusted_to_refined_pedidos_merge",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "trusted", "refined", "pedidos"],
    default_args={
        'retries': 2,
    }
):
    trusted_to_refined = PythonOperator(
        task_id="trusted_to_refined_pedidos_merge",
        python_callable=etl_pedidos_trusted_to_refined,
    )