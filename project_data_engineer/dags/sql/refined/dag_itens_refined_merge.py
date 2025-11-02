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

def _map_row_to_refined_itens(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeamento da TRUSTED para REFINED com conversões de tipo e tratamento de NaN.
    """
    # DEBUG: Log para verificar a estrutura dos dados
    if not hasattr(_map_row_to_refined_itens, 'logged_structure'):
        log.info("Estrutura da linha recebida da TRUSTED: %s", list(row.keys())[:10])
        _map_row_to_refined_itens.logged_structure = True
    
    return {
        "ID_ITEM": _convert_to_varchar(row.get("ITEM"), "-1", "ID_ITEM"),
        "ID_TIPOFT2": _convert_to_varchar(row.get("IDTIPOFT2"), "-1", "ID_TIPOFT2"),
        "ID_FAMILIA": _convert_to_varchar(row.get("IDFAMILIA"), "-1", "ID_FAMILIA"),
        "QT_ESTADOFT_DETEC": _convert_to_number(row.get("ESTADOFT_DETEC"), 0),
        "TX_ESTADOFT_DETEC": _convert_to_varchar(row.get("TEXTOESTADOFT_DETEC"), " ", "TX_ESTADOFT_DETEC"),
        "ST_FT": _convert_to_varchar(row.get("STATUSFT"), " ", "ST_FT"),
        "TX_TATUSFT": _convert_to_varchar(row.get("TEXTOSTATUSFT"), " ", "TX_TATUSFT"),
        "ID_CLIENTE": _convert_to_varchar(row.get("IDCLIENTE"), "-1", "ID_CLIENTE"),
        "TX_REFERENCIA": _convert_to_varchar(row.get("REFERENCIA"), " ", "TX_REFERENCIA"),
        "CD_REFERENCIA": _convert_to_varchar(row.get("CODIGOREFERENCIA"), "-1", "CD_REFERENCIA"),
        "TX_TIPOABNT": _convert_to_varchar(row.get("TIPOABNT"), " ", "TX_TIPOABNT"),
        "FL_EXIGELAUDO": _convert_to_varchar(_handle_nan(row.get("EXIGELAUDO"), 0), "0", "FL_EXIGELAUDO"),
        "VL_GRAMATURA": _convert_to_number(row.get("GRAMATURA"), 0),
        "VL_COLUNAMINIMO": _convert_to_number(row.get("COLUNAMINIMO"), 0),
        "VL_COBBINTMAXIMO": _convert_to_number(row.get("COBBINTMAXIMO"), 0),
        "CD_COMPRESSAO": _convert_to_varchar(row.get("COMPRESSAO"), "-1", "CD_COMPRESSAO"),
        "CD_COMPOSICAO": _convert_to_varchar(row.get("COMPOSICAO"), "-1", "CD_COMPOSICAO"),
        "VL_LARGURA": _convert_to_number(row.get("LARGURA"), 0),
        "VL_REFILOLARGURA": _convert_to_number(row.get("REFILOLARGURA"), 0),
        "VL_COMPRIMENTO": _convert_to_number(row.get("COMPRIMENTO"), 0),
        "VL_REFILOCOMPRIMENTO": _convert_to_number(row.get("REFILOCOMPRIMENTO"), 0),
        "VL_MULTLARG": _convert_to_number(row.get("MULTLARG"), 0),
        "VL_MULTCOMP": _convert_to_number(row.get("MULTCOMP"), 0),
        "VL_ARRANJO": _convert_to_number(row.get("ARRANJO"), 0),
        "VL_REFUGOCLIENTE": _convert_to_number(row.get("REFUGOCLIENTE"), 0),
        "VL_VINCOLARG1": _convert_to_number(row.get("VINCOLARG1"), 0),
        "VL_VINCOLARG2": _convert_to_number(row.get("VINCOLARG2"), 0),
        "VL_VINCOLARG3": _convert_to_number(row.get("VINCOLARG3"), 0),
        "VL_VINCOCOMP1": _convert_to_number(row.get("VINCOCOMP1"), 0),
        "VL_VINCOCOMP2": _convert_to_number(row.get("VINCOCOMP2"), 0),
        "VL_VINCOCOMP3": _convert_to_number(row.get("VINCOCOMP3"), 0),
        "VL_VINCOCOMP4": _convert_to_number(row.get("VINCOCOMP4"), 0),
        "VL_VINCOCOMP5": _convert_to_number(row.get("VINCOCOMP5"), 0),
        "VL_LAP": _convert_to_number(row.get("LAP"), 0),
        "VL_PROLONGLAP": _convert_to_number(row.get("PROLONGLAP"), 0),
        "VL_LAPNOCOMP": _convert_to_number(row.get("LAPNOCOMP"), 0),
        "VL_LAPINTERNO": _convert_to_number(row.get("LAPINTERNO"), 0),
        "FL_REFILADO": _convert_to_varchar(_handle_nan(row.get("REFILADO"), 0), "0", "FL_REFILADO"),
        "FL_RESINAINTERNA": _convert_to_varchar(_handle_nan(row.get("RESINAINTERNA"), 0), "0", "FL_RESINAINTERNA"),
        "FL_AMARRADO": _convert_to_varchar(_handle_nan(row.get("AMARRADO"), 0), "0", "FL_AMARRADO"),
        "FL_PALETIZADO": _convert_to_varchar(_handle_nan(row.get("PALETIZADO"), 0), "0", "FL_PALETIZADO"),
        "VL_PACOTESLARGURA": _convert_to_number(row.get("PACOTESLARGURA"), 0),
        "VL_PACOTESCOMPRIMENTO": _convert_to_number(row.get("PACOTESCOMPRIMENTO"), 0),
        "VL_PACOTESALTURA": _convert_to_number(row.get("PACOTESALTURA"), 0),
        "VL_PECASPORPACOTE": _convert_to_number(row.get("PECASPORPACOTE"), 0),
        "VL_PECASPORPALETE": _convert_to_number(row.get("PECASPORPALETE"), 0),
        "VL_PACOTESPORPALETE": _convert_to_number(row.get("PACOTESPORPALETE"), 0),
        "VL_UNIDADESPORPALETE": _convert_to_number(row.get("UNIDADESPORPALETE"), 0),
        "FL_ESPELHO": _convert_to_varchar(_handle_nan(row.get("ESPELHO"), 0), "0", "FL_ESPELHO"),
        "FL_FILME": _convert_to_varchar(_handle_nan(row.get("FILME"), 0), "0", "FL_FILME"),
        "ID_FACA": _convert_to_varchar(row.get("FACA"), "-1", "ID_FACA"),
        "TX_COR1": _convert_to_varchar(row.get("COR1"), " ", "TX_COR1"),
        "VL_CONSUMOCOR1": _convert_to_number(row.get("CONSUMOCOR1"), 0),
        "TX_COR2": _convert_to_varchar(row.get("COR2"), " ", "TX_COR2"),
        "VL_CONSUMOCOR2": _convert_to_number(row.get("CONSUMOCOR2"), 0),
        "TX_COR3": _convert_to_varchar(row.get("COR3"), " ", "TX_COR3"),
        "VL_CONSUMOCOR3": _convert_to_number(row.get("CONSUMOCOR3"), 0),
        "TX_COR4": _convert_to_varchar(row.get("COR4"), " ", "TX_COR4"),
        "VL_CONSUMOCOR4": _convert_to_number(row.get("CONSUMOCOR4"), 0),
        "QT_NRCORES": _convert_to_number(row.get("NRCORES"), 0),
        "VL_LARGURAINTERNA": _convert_to_number(row.get("LARGURAINTERNA"), 0),
        "VL_COMPRIMENTOINTERNO": _convert_to_number(row.get("COMPRIMENTOINTERNO"), 0),
        "VL_ALTURAINTERNA": _convert_to_number(row.get("ALTURAINTERNA"), 0),
        "VL_LARGPECA": _convert_to_number(row.get("LARGPECA"), 0),
        "VL_COMPPECA": _convert_to_number(row.get("COMPPECA"), 0),
        "VL_COMPPACOTE": _convert_to_number(row.get("COMPPACOTE"), 0),
        "VL_LARGPACOTE": _convert_to_number(row.get("LARGPACOTE"), 0),
        "VL_ALTURAPACOTE": _convert_to_number(row.get("ALTURAPACOTE"), 0),
        "VL_COMMPALETEFECHADO": _convert_to_number(row.get("COMMPALETEFECHADO"), 0),
        "VL_LARGPALETEFECHADO": _convert_to_number(row.get("LARGPALETEFECHADO"), 0),
        "VL_ALTURAPALETEFECHADO": _convert_to_number(row.get("ALTURAPALETEFECHADO"), 0),
        "VL_PESOCAIXA": _convert_to_number(row.get("PESOCAIXA"), 0),
        "TX_PATHFIGURADOLASTRO": _convert_to_varchar(row.get("PATHFIGURADOLASTRO"), " ", "TX_PATHFIGURADOLASTRO"),
        "ID_PALETE": _convert_to_varchar(row.get("IDPALETE"), "-1", "ID_PALETE"),
        "VL_AREABRUTAPECACOMREFILOS": _convert_to_number(row.get("AREABRUTAPECACOMREFILOS"), 0),
        "VL_AREABRUTAPECA": _convert_to_number(row.get("AREABRUTAPECA"), 0),
        "VL_AREALIQUIDAPECA": _convert_to_number(row.get("AREALIQUIDAPECA"), 0),
        "VL_AREABRUTACHAPA": _convert_to_number(row.get("AREABRUTACHAPA"), 0),
        "VL_AREALIQUIDACHAPA": _convert_to_number(row.get("AREALIQUIDACHAPA"), 0),
        "VL_VOLUMEPALETEFECHADOM3": _convert_to_number(row.get("VOLUMEPALETEFECHADOM3"), 0),
        "VL_VOLUMEPACOTEFECHADOM3": _convert_to_number(row.get("VOLUMEPACOTEFECHADOM3"), 0),
    }

# -----------------
# Tarefa principal
# -----------------
def etl_itens_trusted_to_refined(**context):
    # Configuração de paginação - 40.000 registros por lote
    page_size = 100000
    offset = 0
    total_processed = 0
    batch_count = 0
    
    # REMOVIDO O TRUNCATE - dados serao preservados na tabela destino

    # Loop de paginação
    while True:
        # Query com paginação da tabela TRUSTED
        sql = """
            SELECT * FROM ITENS 
            ORDER BY ITEM
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
            
            log.info("TRUSTED -> Página %s: %s registros extraídos da tabela ITENS.", 
                    batch_count + 1, len(rows))

            if not rows:
                log.info("Todas as páginas processadas. Total: %s registros.", total_processed)
                break

            # 2) Mapeia para o layout do REFINED
            payload = []
            mapping_errors = 0
            
            for r in rows:
                try:
                    mapped_row = _map_row_to_refined_itens(r)
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
                
                # 3) Processa o lote atual com MERGE
                _process_batch_itens_refined_merge(payload, batch_count + 1)
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

def _process_batch_itens_refined_merge(payload, batch_number):
    """Processa um lote de registros no Oracle REFINED com MERGE"""
    merge_sql = """
        MERGE INTO ITENS dest
        USING (
            SELECT 
                :ID_ITEM as ID_ITEM,
                :ID_TIPOFT2 as ID_TIPOFT2,
                :ID_FAMILIA as ID_FAMILIA,
                :QT_ESTADOFT_DETEC as QT_ESTADOFT_DETEC,
                :TX_ESTADOFT_DETEC as TX_ESTADOFT_DETEC,
                :ST_FT as ST_FT,
                :TX_TATUSFT as TX_TATUSFT,
                :ID_CLIENTE as ID_CLIENTE,
                :TX_REFERENCIA as TX_REFERENCIA,
                :CD_REFERENCIA as CD_REFERENCIA,
                :TX_TIPOABNT as TX_TIPOABNT,
                :FL_EXIGELAUDO as FL_EXIGELAUDO,
                :VL_GRAMATURA as VL_GRAMATURA,
                :VL_COLUNAMINIMO as VL_COLUNAMINIMO,
                :VL_COBBINTMAXIMO as VL_COBBINTMAXIMO,
                :CD_COMPRESSAO as CD_COMPRESSAO,
                :CD_COMPOSICAO as CD_COMPOSICAO,
                :VL_LARGURA as VL_LARGURA,
                :VL_REFILOLARGURA as VL_REFILOLARGURA,
                :VL_COMPRIMENTO as VL_COMPRIMENTO,
                :VL_REFILOCOMPRIMENTO as VL_REFILOCOMPRIMENTO,
                :VL_MULTLARG as VL_MULTLARG,
                :VL_MULTCOMP as VL_MULTCOMP,
                :VL_ARRANJO as VL_ARRANJO,
                :VL_REFUGOCLIENTE as VL_REFUGOCLIENTE,
                :VL_VINCOLARG1 as VL_VINCOLARG1,
                :VL_VINCOLARG2 as VL_VINCOLARG2,
                :VL_VINCOLARG3 as VL_VINCOLARG3,
                :VL_VINCOCOMP1 as VL_VINCOCOMP1,
                :VL_VINCOCOMP2 as VL_VINCOCOMP2,
                :VL_VINCOCOMP3 as VL_VINCOCOMP3,
                :VL_VINCOCOMP4 as VL_VINCOCOMP4,
                :VL_VINCOCOMP5 as VL_VINCOCOMP5,
                :VL_LAP as VL_LAP,
                :VL_PROLONGLAP as VL_PROLONGLAP,
                :VL_LAPNOCOMP as VL_LAPNOCOMP,
                :VL_LAPINTERNO as VL_LAPINTERNO,
                :FL_REFILADO as FL_REFILADO,
                :FL_RESINAINTERNA as FL_RESINAINTERNA,
                :FL_AMARRADO as FL_AMARRADO,
                :FL_PALETIZADO as FL_PALETIZADO,
                :VL_PACOTESLARGURA as VL_PACOTESLARGURA,
                :VL_PACOTESCOMPRIMENTO as VL_PACOTESCOMPRIMENTO,
                :VL_PACOTESALTURA as VL_PACOTESALTURA,
                :VL_PECASPORPACOTE as VL_PECASPORPACOTE,
                :VL_PECASPORPALETE as VL_PECASPORPALETE,
                :VL_PACOTESPORPALETE as VL_PACOTESPORPALETE,
                :VL_UNIDADESPORPALETE as VL_UNIDADESPORPALETE,
                :FL_ESPELHO as FL_ESPELHO,
                :FL_FILME as FL_FILME,
                :ID_FACA as ID_FACA,
                :TX_COR1 as TX_COR1,
                :VL_CONSUMOCOR1 as VL_CONSUMOCOR1,
                :TX_COR2 as TX_COR2,
                :VL_CONSUMOCOR2 as VL_CONSUMOCOR2,
                :TX_COR3 as TX_COR3,
                :VL_CONSUMOCOR3 as VL_CONSUMOCOR3,
                :TX_COR4 as TX_COR4,
                :VL_CONSUMOCOR4 as VL_CONSUMOCOR4,
                :QT_NRCORES as QT_NRCORES,
                :VL_LARGURAINTERNA as VL_LARGURAINTERNA,
                :VL_COMPRIMENTOINTERNO as VL_COMPRIMENTOINTERNO,
                :VL_ALTURAINTERNA as VL_ALTURAINTERNA,
                :VL_LARGPECA as VL_LARGPECA,
                :VL_COMPPECA as VL_COMPPECA,
                :VL_COMPPACOTE as VL_COMPPACOTE,
                :VL_LARGPACOTE as VL_LARGPACOTE,
                :VL_ALTURAPACOTE as VL_ALTURAPACOTE,
                :VL_COMMPALETEFECHADO as VL_COMMPALETEFECHADO,
                :VL_LARGPALETEFECHADO as VL_LARGPALETEFECHADO,
                :VL_ALTURAPALETEFECHADO as VL_ALTURAPALETEFECHADO,
                :VL_PESOCAIXA as VL_PESOCAIXA,
                :TX_PATHFIGURADOLASTRO as TX_PATHFIGURADOLASTRO,
                :ID_PALETE as ID_PALETE,
                :VL_AREABRUTAPECACOMREFILOS as VL_AREABRUTAPECACOMREFILOS,
                :VL_AREABRUTAPECA as VL_AREABRUTAPECA,
                :VL_AREALIQUIDAPECA as VL_AREALIQUIDAPECA,
                :VL_AREABRUTACHAPA as VL_AREABRUTACHAPA,
                :VL_AREALIQUIDACHAPA as VL_AREALIQUIDACHAPA,
                :VL_VOLUMEPALETEFECHADOM3 as VL_VOLUMEPALETEFECHADOM3,
                :VL_VOLUMEPACOTEFECHADOM3 as VL_VOLUMEPACOTEFECHADOM3
            FROM DUAL
        ) src
        ON (dest.ID_ITEM = src.ID_ITEM)
        WHEN MATCHED THEN
            UPDATE SET 
                ID_TIPOFT2 = src.ID_TIPOFT2,
                ID_FAMILIA = src.ID_FAMILIA,
                QT_ESTADOFT_DETEC = src.QT_ESTADOFT_DETEC,
                TX_ESTADOFT_DETEC = src.TX_ESTADOFT_DETEC,
                ST_FT = src.ST_FT,
                TX_TATUSFT = src.TX_TATUSFT,
                ID_CLIENTE = src.ID_CLIENTE,
                TX_REFERENCIA = src.TX_REFERENCIA,
                CD_REFERENCIA = src.CD_REFERENCIA,
                TX_TIPOABNT = src.TX_TIPOABNT,
                FL_EXIGELAUDO = src.FL_EXIGELAUDO,
                VL_GRAMATURA = src.VL_GRAMATURA,
                VL_COLUNAMINIMO = src.VL_COLUNAMINIMO,
                VL_COBBINTMAXIMO = src.VL_COBBINTMAXIMO,
                CD_COMPRESSAO = src.CD_COMPRESSAO,
                CD_COMPOSICAO = src.CD_COMPOSICAO,
                VL_LARGURA = src.VL_LARGURA,
                VL_REFILOLARGURA = src.VL_REFILOLARGURA,
                VL_COMPRIMENTO = src.VL_COMPRIMENTO,
                VL_REFILOCOMPRIMENTO = src.VL_REFILOCOMPRIMENTO,
                VL_MULTLARG = src.VL_MULTLARG,
                VL_MULTCOMP = src.VL_MULTCOMP,
                VL_ARRANJO = src.VL_ARRANJO,
                VL_REFUGOCLIENTE = src.VL_REFUGOCLIENTE,
                VL_VINCOLARG1 = src.VL_VINCOLARG1,
                VL_VINCOLARG2 = src.VL_VINCOLARG2,
                VL_VINCOLARG3 = src.VL_VINCOLARG3,
                VL_VINCOCOMP1 = src.VL_VINCOCOMP1,
                VL_VINCOCOMP2 = src.VL_VINCOCOMP2,
                VL_VINCOCOMP3 = src.VL_VINCOCOMP3,
                VL_VINCOCOMP4 = src.VL_VINCOCOMP4,
                VL_VINCOCOMP5 = src.VL_VINCOCOMP5,
                VL_LAP = src.VL_LAP,
                VL_PROLONGLAP = src.VL_PROLONGLAP,
                VL_LAPNOCOMP = src.VL_LAPNOCOMP,
                VL_LAPINTERNO = src.VL_LAPINTERNO,
                FL_REFILADO = src.FL_REFILADO,
                FL_RESINAINTERNA = src.FL_RESINAINTERNA,
                FL_AMARRADO = src.FL_AMARRADO,
                FL_PALETIZADO = src.FL_PALETIZADO,
                VL_PACOTESLARGURA = src.VL_PACOTESLARGURA,
                VL_PACOTESCOMPRIMENTO = src.VL_PACOTESCOMPRIMENTO,
                VL_PACOTESALTURA = src.VL_PACOTESALTURA,
                VL_PECASPORPACOTE = src.VL_PECASPORPACOTE,
                VL_PECASPORPALETE = src.VL_PECASPORPALETE,
                VL_PACOTESPORPALETE = src.VL_PACOTESPORPALETE,
                VL_UNIDADESPORPALETE = src.VL_UNIDADESPORPALETE,
                FL_ESPELHO = src.FL_ESPELHO,
                FL_FILME = src.FL_FILME,
                ID_FACA = src.ID_FACA,
                TX_COR1 = src.TX_COR1,
                VL_CONSUMOCOR1 = src.VL_CONSUMOCOR1,
                TX_COR2 = src.TX_COR2,
                VL_CONSUMOCOR2 = src.VL_CONSUMOCOR2,
                TX_COR3 = src.TX_COR3,
                VL_CONSUMOCOR3 = src.VL_CONSUMOCOR3,
                TX_COR4 = src.TX_COR4,
                VL_CONSUMOCOR4 = src.VL_CONSUMOCOR4,
                QT_NRCORES = src.QT_NRCORES,
                VL_LARGURAINTERNA = src.VL_LARGURAINTERNA,
                VL_COMPRIMENTOINTERNO = src.VL_COMPRIMENTOINTERNO,
                VL_ALTURAINTERNA = src.VL_ALTURAINTERNA,
                VL_LARGPECA = src.VL_LARGPECA,
                VL_COMPPECA = src.VL_COMPPECA,
                VL_COMPPACOTE = src.VL_COMPPACOTE,
                VL_LARGPACOTE = src.VL_LARGPACOTE,
                VL_ALTURAPACOTE = src.VL_ALTURAPACOTE,
                VL_COMMPALETEFECHADO = src.VL_COMMPALETEFECHADO,
                VL_LARGPALETEFECHADO = src.VL_LARGPALETEFECHADO,
                VL_ALTURAPALETEFECHADO = src.VL_ALTURAPALETEFECHADO,
                VL_PESOCAIXA = src.VL_PESOCAIXA,
                TX_PATHFIGURADOLASTRO = src.TX_PATHFIGURADOLASTRO,
                ID_PALETE = src.ID_PALETE,
                VL_AREABRUTAPECACOMREFILOS = src.VL_AREABRUTAPECACOMREFILOS,
                VL_AREABRUTAPECA = src.VL_AREABRUTAPECA,
                VL_AREALIQUIDAPECA = src.VL_AREALIQUIDAPECA,
                VL_AREABRUTACHAPA = src.VL_AREABRUTACHAPA,
                VL_AREALIQUIDACHAPA = src.VL_AREALIQUIDACHAPA,
                VL_VOLUMEPALETEFECHADOM3 = src.VL_VOLUMEPALETEFECHADOM3,
                VL_VOLUMEPACOTEFECHADOM3 = src.VL_VOLUMEPACOTEFECHADOM3
        WHEN NOT MATCHED THEN
            INSERT (
                ID_ITEM, ID_TIPOFT2, ID_FAMILIA, QT_ESTADOFT_DETEC, TX_ESTADOFT_DETEC, ST_FT, TX_TATUSFT,
                ID_CLIENTE, TX_REFERENCIA, CD_REFERENCIA, TX_TIPOABNT, FL_EXIGELAUDO, VL_GRAMATURA,
                VL_COLUNAMINIMO, VL_COBBINTMAXIMO, CD_COMPRESSAO, CD_COMPOSICAO, VL_LARGURA, VL_REFILOLARGURA,
                VL_COMPRIMENTO, VL_REFILOCOMPRIMENTO, VL_MULTLARG, VL_MULTCOMP, VL_ARRANJO, VL_REFUGOCLIENTE,
                VL_VINCOLARG1, VL_VINCOLARG2, VL_VINCOLARG3, VL_VINCOCOMP1, VL_VINCOCOMP2, VL_VINCOCOMP3,
                VL_VINCOCOMP4, VL_VINCOCOMP5, VL_LAP, VL_PROLONGLAP, VL_LAPNOCOMP, VL_LAPINTERNO, FL_REFILADO,
                FL_RESINAINTERNA, FL_AMARRADO, FL_PALETIZADO, VL_PACOTESLARGURA, VL_PACOTESCOMPRIMENTO,
                VL_PACOTESALTURA, VL_PECASPORPACOTE, VL_PECASPORPALETE, VL_PACOTESPORPALETE, VL_UNIDADESPORPALETE,
                FL_ESPELHO, FL_FILME, ID_FACA, TX_COR1, VL_CONSUMOCOR1, TX_COR2, VL_CONSUMOCOR2, TX_COR3,
                VL_CONSUMOCOR3, TX_COR4, VL_CONSUMOCOR4, QT_NRCORES, VL_LARGURAINTERNA, VL_COMPRIMENTOINTERNO,
                VL_ALTURAINTERNA, VL_LARGPECA, VL_COMPPECA, VL_COMPPACOTE, VL_LARGPACOTE, VL_ALTURAPACOTE,
                VL_COMMPALETEFECHADO, VL_LARGPALETEFECHADO, VL_ALTURAPALETEFECHADO, VL_PESOCAIXA,
                TX_PATHFIGURADOLASTRO, ID_PALETE, VL_AREABRUTAPECACOMREFILOS, VL_AREABRUTAPECA, VL_AREALIQUIDAPECA,
                VL_AREABRUTACHAPA, VL_AREALIQUIDACHAPA, VL_VOLUMEPALETEFECHADOM3, VL_VOLUMEPACOTEFECHADOM3
            ) VALUES (
                src.ID_ITEM, src.ID_TIPOFT2, src.ID_FAMILIA, src.QT_ESTADOFT_DETEC, src.TX_ESTADOFT_DETEC, src.ST_FT, src.TX_TATUSFT,
                src.ID_CLIENTE, src.TX_REFERENCIA, src.CD_REFERENCIA, src.TX_TIPOABNT, src.FL_EXIGELAUDO, src.VL_GRAMATURA,
                src.VL_COLUNAMINIMO, src.VL_COBBINTMAXIMO, src.CD_COMPRESSAO, src.CD_COMPOSICAO, src.VL_LARGURA, src.VL_REFILOLARGURA,
                src.VL_COMPRIMENTO, src.VL_REFILOCOMPRIMENTO, src.VL_MULTLARG, src.VL_MULTCOMP, src.VL_ARRANJO, src.VL_REFUGOCLIENTE,
                src.VL_VINCOLARG1, src.VL_VINCOLARG2, src.VL_VINCOLARG3, src.VL_VINCOCOMP1, src.VL_VINCOCOMP2, src.VL_VINCOCOMP3,
                src.VL_VINCOCOMP4, src.VL_VINCOCOMP5, src.VL_LAP, src.VL_PROLONGLAP, src.VL_LAPNOCOMP, src.VL_LAPINTERNO, src.FL_REFILADO,
                src.FL_RESINAINTERNA, src.FL_AMARRADO, src.FL_PALETIZADO, src.VL_PACOTESLARGURA, src.VL_PACOTESCOMPRIMENTO,
                src.VL_PACOTESALTURA, src.VL_PECASPORPACOTE, src.VL_PECASPORPALETE, src.VL_PACOTESPORPALETE, src.VL_UNIDADESPORPALETE,
                src.FL_ESPELHO, src.FL_FILME, src.ID_FACA, src.TX_COR1, src.VL_CONSUMOCOR1, src.TX_COR2, src.VL_CONSUMOCOR2, src.TX_COR3,
                src.VL_CONSUMOCOR3, src.TX_COR4, src.VL_CONSUMOCOR4, src.QT_NRCORES, src.VL_LARGURAINTERNA, src.VL_COMPRIMENTOINTERNO,
                src.VL_ALTURAINTERNA, src.VL_LARGPECA, src.VL_COMPPECA, src.VL_COMPPACOTE, src.VL_LARGPACOTE, src.VL_ALTURAPACOTE,
                src.VL_COMMPALETEFECHADO, src.VL_LARGPALETEFECHADO, src.VL_ALTURAPALETEFECHADO, src.VL_PESOCAIXA,
                src.TX_PATHFIGURADOLASTRO, src.ID_PALETE, src.VL_AREABRUTAPECACOMREFILOS, src.VL_AREABRUTAPECA, src.VL_AREALIQUIDAPECA,
                src.VL_AREABRUTACHAPA, src.VL_AREALIQUIDACHAPA, src.VL_VOLUMEPALETEFECHADOM3, src.VL_VOLUMEPACOTEFECHADOM3
            )
    """

    dst = _make_oracle_conn_refined()
    try:
        cur = dst.cursor()
        
        # Executa o MERGE para cada registro
        success_count = 0
        error_count = 0
        
        for record in payload:
            try:
                cur.execute(merge_sql, record)
                success_count += 1
            except Exception as e:
                log.error("Erro ao processar registro no MERGE (lote %s): %s", batch_number, str(e))
                error_count += 1
                # Continua processando os demais registros
        
        dst.commit()
        log.info("REFINED <- Lote %s: %s registros processados com sucesso, %s erros.", batch_number, success_count, error_count)
            
    except Exception as e:
        log.error("Erro ao executar MERGE no Oracle REFINED (lote %s): %s", batch_number, str(e))
        dst.rollback()
        raise
    finally:
        dst.close()

# -----------------
# DAG
# -----------------
with DAG(
    dag_id="etl_trusted_to_refined_itens_merge",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "trusted", "refined", "itens"],
    default_args={
        'retries': 2,
    }
):
    trusted_to_refined = PythonOperator(
        task_id="trusted_to_refined_itens",
        python_callable=etl_itens_trusted_to_refined,
    )