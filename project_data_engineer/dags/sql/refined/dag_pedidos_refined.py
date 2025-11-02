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
    
    # 1) TRUNCATE na tabela de destino REFINED
    log.info("REFINED -> Executando TRUNCATE na tabela PEDIDOS...")
    dst_conn = _make_oracle_conn_refined()
    try:
        with dst_conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE PEDIDOS")
        dst_conn.commit()
        log.info("REFINED -> TRUNCATE executado com sucesso na tabela PEDIDOS.")
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
    """Processa um lote de registros no Oracle REFINED com INSERT direto"""
    insert_sql = """
        INSERT INTO PEDIDOS (
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
            :CD_ESPELHO, :CD_FACA, :CD_FILME, :CD_LAPINTERNO, :CD_LAPNOCOMP, :CD_REFERENCIA,
            :DT_ENTREGA2, :DT_ENTREGAORIGINAL, :FL_AMARRADO, :FL_CHAPA, :TX_COR3, :TX_COR4,
            :FL_EXIGELAUDO, :FL_PALETIZADO, :FL_REFILADO, :FL_RESINAINTERNA, :FL_SUSPENSO,
            :TX_SUSPOUCANCEL, :FL_TIPOENTREGA, :ID_CLIENTE, :ID_ITEM, :ID_PALETE, :ID_PEDIDO,
            :ID_TIPOFT2, :QT_ARRANJO, :QT_COBBINTMAXIMO, :QT_LAP, :QT_NRCORES, :QT_PACOTESPORPALETE,
            :QT_PECASPORPACOTE, :QT_PECASPORPALETE, :QT_PEDIDA, :QT_PEDIDAMAX, :QT_PEDIDAMIN,
            :QT_PROLONGLAP, :QT_UNIDADESPORPALETE, :ST_PEDIDO, :TX_COMPOSICAO, :TX_COR1, :TX_COR2,
            :TX_DESCRSTATUSPEDIDO, :TX_DESCRTIPODOPEDIDO, :TX_DESCTIPOENTREGA, :TX_PATHFIGURADOLASTRO,
            :TX_REFERENCIA, :TX_TIPOABNT, :VL_ALTURAINTERNA, :VL_ALTURAPACOTE, :VL_ALTURAPALETEFECHADO,
            :VL_AREABRUTACHAPA, :VL_AREABRUTAPECA, :VL_AREABRUTAPECACOMREFILOS, :VL_AREALIQUIDACHAPA,
            :VL_AREALIQUIDAPECA, :VL_COLUNAMINIMO, :VL_COMPPACOTE, :VL_COMPPALETEFECHADO, :VL_COMPPECA,
            :VL_COMPRESSAO, :VL_COMPRIMENTO, :VL_COMPRIMENTOINTERNO, :VL_CONSUMOCOR1, :VL_CONSUMOCOR2,
            :VL_CONSUMOCOR3, :VL_CONSUMOCOR4, :VL_GRAMATURA, :VL_LARGPACOTE, :VL_LARGPALETEFECHADO,
            :VL_LARGPECA, :VL_LARGURA, :VL_LARGURAINTERNA, :VL_MULTCOMP, :VL_MULTLARG, :VL_PACOTESALTURA,
            :VL_PACOTESCOMPRIMENTO, :VL_PACOTESLARGURA, :VL_PESOCAIXA, :VL_PESOPECA, :VL_REFILOCOMPRIMENTO,
            :VL_REFILOLARGURA, :VL_REFUGOCLIENTE, :VL_VINCOCOMP1, :VL_VINCOCOMP2, :VL_VINCOCOMP3,
            :VL_VINCOCOMP4, :VL_VINCOCOMP5, :VL_VINCOLARG1, :VL_VINCOLARG2, :VL_VINCOLARG3,
            :VL_VOLUMEFECHADOPEDIDO, :VL_VOLUMEPACOTEFECHADOM3, :VL_VOLUMEPALETEFECHADOM3
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
    dag_id="etl_trusted_to_refined_pedidos",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "trusted", "refined", "pedidos"],
    default_args={
        'retries': 2,
    }
):
    trusted_to_refined = PythonOperator(
        task_id="trusted_to_refined_pedidos",
        python_callable=etl_pedidos_trusted_to_refined,
    )