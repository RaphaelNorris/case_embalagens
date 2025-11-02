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

def _guid_to_raw16(v: Any):
    if v is None:
        return None
    if isinstance(v, (bytes, bytearray)) and len(v) == 16:
        return bytes(v)
    s = str(v).strip().lower().replace("-", "")
    if len(s) != 32:
        return None
    return binascii.unhexlify(s)

def _convert_to_timestamp6(value):
    """
    Converte para TIMESTAMP(6) do Oracle mantendo hora, minuto, segundo e microssegundos.
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

def _map_row_to_oracle(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeamento das colunas do SQL Server para Oracle.
    """
    return {
        "IDCLIENTE": row.get("IDCliente"),
        "CLIENTE": row.get("Cliente"),
        "CODCLIENTE": row.get("CodCliente"),
        "CODREPRESENTANTE": row.get("CodRepresentante"),
        "TOLMAIS": row.get("TolMais"),
        "TOLMENOS": row.get("TolMenos"),
        "TIPOOBS1": row.get("TipoObs1"),
        "OBS1": row.get("Obs1"),
        "TIPOOBS2": row.get("TipoObs2"),
        "OBS2": row.get("Obs2"),
        "TIPOOBS3": row.get("TipoObs3"),
        "OBS3": row.get("Obs3"),
        "TIPOOBS4": row.get("TipoObs4"),
        "OBS4": row.get("Obs4"),
        "TIPOABC": row.get("TipoABC"),
        "CODSEGMENTO": row.get("CodSegmento"),
        "PREFERENCIALSN": _bit_to_char(row.get("PreferencialSN")),
        "CLIENTELISTASN": _bit_to_char(row.get("ClienteListaSN")),
        "AGRUPAMENTO": row.get("Agrupamento"),
        "CLIENTE_FORNECEDOR": row.get("Cliente_Fornecedor"),
        "DESCRCLIENTE_FORNECEDOR": row.get("DescrCliente_Fornecedor"),
        "RAZAOSOCIAL": row.get("RazaoSocial"),
        "CODIGOERP": row.get("CodigoERP"),
        "ETIQUETA": row.get("Etiqueta"),
        "EXIGELAUDO": _bit_to_char(row.get("ExigeLaudo")),
        "LAUDO": row.get("Laudo"),
        "EMAILLAUDO": row.get("EmailLaudo"),
        "CARTAORCAMENTO": row.get("CartaOrcamento"),
        "NRETIQUETAS": row.get("NrEtiquetas"),
        "IDUNICOREGISTRO": _guid_to_raw16(row.get("IDUnicoRegistro")),
        "ACEITAPALETEINCOMPLETO": row.get("AceitaPaleteIncompleto"),
        "DESCACEITAPALETEINCOMPLETO": row.get("DescAceitaPaleteIncompleto"),
        "IDATENDENTEVENDA": row.get("idAtendenteVenda"),
        "CONTATOFATURAMENTO": row.get("ContatoFaturamento"),
        "IDCLASSFISCAL": row.get("IDClassFiscal"),
        "DATACRIACAO": _convert_to_timestamp6(row.get("DataCriacao")),  # CORRIGIDO para TIMESTAMP(6)
        "USUARIOCRIACAO": row.get("UsuarioCriacao"),
        "DATAULTMODIF": _convert_to_timestamp6(row.get("DataUltModif")),  # CORRIGIDO para TIMESTAMP(6)
        "USUARIOULTMODIF": row.get("UsuarioUltModif"),
        "RAZAOTRAVACOMPOSICAO": row.get("RazaoTravaComposicao"),
        "CUSTOFINANCEIROADICIONAL": row.get("CustoFinanceiroAdicional"),
        "CUSTOADICTRANSPORTEPORPALETE": row.get("CustoAdicTransportePorPalete"),
        "CUSTOADICTRANSPPORKG_PALETIZ": row.get("CustoAdicTransportePorKg_Paletizado"),
        "CUSTOADICTRANSPPORKG_NPALETIZ": row.get("CustoAdicTransportePorKg_NaoPaletizado"),
        "CUSTOADICTRANSPPORM2_PALETIZ": row.get("CustoAdicTransportePorM2_Paletizado"),
        "CUSTOADICTRANSPPORM2_NPALETIZ": row.get("CustoAdicTransportePorM2_NaoPaletizado"),
        "CUSTOADICTRANSPPORPECA_PALETIZ": row.get("CustoAdicTransportePorPeca_Paletizado"),
        "CUSTOADICTRANSPPORPECANPALETIZ": row.get("CustoAdicTransportePorPeca_NaoPaletizado"),
        "USOGERALSTR1": row.get("UsoGeralStr1"),
        "USOGERALSTR2": row.get("UsoGeralStr2"),
        "USOGERALNUM1": row.get("UsoGeralNum1"),
        "USOGERALNUM2": row.get("UsoGeralNum2"),
        "EXIGECHAPAUNITIZADA": _bit_to_char(row.get("ExigeChapaUnitizada")),
        "EXIGEAGENDAMENTOENTREGAS": _bit_to_char(row.get("ExigeAgendamentoEntregas")),
        "CLIENTEPROSPECTO": _bit_to_char(row.get("ClienteProspecto")),
        "IMPRIMELOGOTIPO": _bit_to_char(row.get("ImprimeLogotipo")),
        "PALETIZADO": row.get("Paletizado"),
        "FACESOPPOSTAS": row.get("FacesOpostas"),
        "ESPELHO": row.get("Espelho"),
        "CANTONEIRAS": row.get("Cantoneiras"),
        "FILME": row.get("Filme"),
        "ORELHASINVERTIDAS": row.get("OrelhasInvertidas"),
        "PACOTESLARGURA": row.get("PacotesLargura"),
        "PACOTOSCOMPRIMENTO": row.get("PacotesComprimento"),
        "PACOTESALTURA": row.get("PacotesAltura"),
        "IDPALETE": row.get("IDPalete"),
        "EMPILHAMENTOMAXIMO": row.get("EmpilhamentoMaximo"),
        "PRESSAODEARQUEAMENTO": row.get("PressaoDeArqueamento"),
        "FITASLARGPALETE": row.get("FitasLargPalete"),
        "FITASCOMMPALETE": row.get("FitasCompPalete"),
    }

# -----------------
# Tarefa principal
# -----------------
def etl_clientes(**context):
    # 1) Extrai do SQL Server
    sql = "SELECT * FROM CLIENTES"
    src_conn = _make_mssql_conn()
    try:
        with src_conn.cursor() as cur:
            cur.execute(sql)
            columns = [column[0] for column in cur.description]
            rows = []
            for row in cur.fetchall():
                rows.append(dict(zip(columns, row)))
        log.info("SQL Server -> %s registros extraídos.", len(rows))
        
        # Log para debug - verificar como as datas estão vindo
        if rows:
            sample_row = rows[0]
            log.info("Exemplo de DataCriacao na origem: %s (tipo: %s)", 
                    sample_row.get("DataCriacao"), 
                    type(sample_row.get("DataCriacao")))
            log.info("Exemplo de DataUltModif na origem: %s (tipo: %s)", 
                    sample_row.get("DataUltModif"), 
                    type(sample_row.get("DataUltModif")))
            
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
            mapped_row = _map_row_to_oracle(r)
            
            # Log para debug - verificar como as datas ficaram após mapeamento
            if not payload:  # Apenas no primeiro registro
                log.info("Exemplo de DATACRIACAO após mapeamento: %s (tipo: %s)", 
                        mapped_row.get("DATACRIACAO"), 
                        type(mapped_row.get("DATACRIACAO")))
                log.info("Exemplo de DATAULTMODIF após mapeamento: %s (tipo: %s)", 
                        mapped_row.get("DATAULTMODIF"), 
                        type(mapped_row.get("DATAULTMODIF")))
            
            payload.append(mapped_row)
        except Exception as e:
            log.warning("Erro ao mapear linha: %s. Linha ignorada.", str(e))
            continue

    if not payload:
        log.info("Nenhum dado válido para processar após mapeamento.")
        return

    # 3) MERGE no Oracle
    merge_sql = """
        MERGE INTO CLIENTES T
        USING (
            SELECT
                :IDCLIENTE IDCLIENTE,
                :CLIENTE CLIENTE,
                :CODCLIENTE CODCLIENTE,
                :CODREPRESENTANTE CODREPRESENTANTE,
                :TOLMAIS TOLMAIS,
                :TOLMENOS TOLMENOS,
                :TIPOOBS1 TIPOOBS1,
                :OBS1 OBS1,
                :TIPOOBS2 TIPOOBS2,
                :OBS2 OBS2,
                :TIPOOBS3 TIPOOBS3,
                :OBS3 OBS3,
                :TIPOOBS4 TIPOOBS4,
                :OBS4 OBS4,
                :TIPOABC TIPOABC,
                :CODSEGMENTO CODSEGMENTO,
                :PREFERENCIALSN PREFERENCIALSN,
                :CLIENTELISTASN CLIENTELISTASN,
                :AGRUPAMENTO AGRUPAMENTO,
                :CLIENTE_FORNECEDOR CLIENTE_FORNECEDOR,
                :DESCRCLIENTE_FORNECEDOR DESCRCLIENTE_FORNECEDOR,
                :RAZAOSOCIAL RAZAOSOCIAL,
                :CODIGOERP CODIGOERP,
                :ETIQUETA ETIQUETA,
                :EXIGELAUDO EXIGELAUDO,
                :LAUDO LAUDO,
                :EMAILLAUDO EMAILLAUDO,
                :CARTAORCAMENTO CARTAORCAMENTO,
                :NRETIQUETAS NRETIQUETAS,
                :IDUNICOREGISTRO IDUNICOREGISTRO,
                :ACEITAPALETEINCOMPLETO ACEITAPALETEINCOMPLETO,
                :DESCACEITAPALETEINCOMPLETO DESCACEITAPALETEINCOMPLETO,
                :IDATENDENTEVENDA IDATENDENTEVENDA,
                :CONTATOFATURAMENTO CONTATOFATURAMENTO,
                :IDCLASSFISCAL IDCLASSFISCAL,
                :DATACRIACAO DATACRIACAO,
                :USUARIOCRIACAO USUARIOCRIACAO,
                :DATAULTMODIF DATAULTMODIF,
                :USUARIOULTMODIF USUARIOULTMODIF,
                :RAZAOTRAVACOMPOSICAO RAZAOTRAVACOMPOSICAO,
                :CUSTOFINANCEIROADICIONAL CUSTOFINANCEIROADICIONAL,
                :CUSTOADICTRANSPORTEPORPALETE CUSTOADICTRANSPORTEPORPALETE,
                :CUSTOADICTRANSPPORKG_PALETIZ CUSTOADICTRANSPPORKG_PALETIZ,
                :CUSTOADICTRANSPPORKG_NPALETIZ CUSTOADICTRANSPPORKG_NPALETIZ,
                :CUSTOADICTRANSPPORM2_PALETIZ CUSTOADICTRANSPPORM2_PALETIZ,
                :CUSTOADICTRANSPPORM2_NPALETIZ CUSTOADICTRANSPPORM2_NPALETIZ,
                :CUSTOADICTRANSPPORPECA_PALETIZ CUSTOADICTRANSPPORPECA_PALETIZ,
                :CUSTOADICTRANSPPORPECANPALETIZ CUSTOADICTRANSPPORPECANPALETIZ,
                :USOGERALSTR1 USOGERALSTR1,
                :USOGERALSTR2 USOGERALSTR2,
                :USOGERALNUM1 USOGERALNUM1,
                :USOGERALNUM2 USOGERALNUM2,
                :EXIGECHAPAUNITIZADA EXIGECHAPAUNITIZADA,
                :EXIGEAGENDAMENTOENTREGAS EXIGEAGENDAMENTOENTREGAS,
                :CLIENTEPROSPECTO CLIENTEPROSPECTO,
                :IMPRIMELOGOTIPO IMPRIMELOGOTIPO,
                :PALETIZADO PALETIZADO,
                :FACESOPPOSTAS FACESOPPOSTAS,
                :ESPELHO ESPELHO,
                :CANTONEIRAS CANTONEIRAS,
                :FILME FILME,
                :ORELHASINVERTIDAS ORELHASINVERTIDAS,
                :PACOTESLARGURA PACOTESLARGURA,
                :PACOTOSCOMPRIMENTO PACOTOSCOMPRIMENTO,
                :PACOTESALTURA PACOTESALTURA,
                :IDPALETE IDPALETE,
                :EMPILHAMENTOMAXIMO EMPILHAMENTOMAXIMO,
                :PRESSAODEARQUEAMENTO PRESSAODEARQUEAMENTO,
                :FITASLARGPALETE FITASLARGPALETE,
                :FITASCOMMPALETE FITASCOMMPALETE
            FROM dual
        ) S
        ON (T.IDCLIENTE = S.IDCLIENTE)
        WHEN MATCHED THEN UPDATE SET
            T.CLIENTE = S.CLIENTE,
            T.CODCLIENTE = S.CODCLIENTE,
            T.CODREPRESENTANTE = S.CODREPRESENTANTE,
            T.TOLMAIS = S.TOLMAIS,
            T.TOLMENOS = S.TOLMENOS,
            T.TIPOOBS1 = S.TIPOOBS1,
            T.OBS1 = S.OBS1,
            T.TIPOOBS2 = S.TIPOOBS2,
            T.OBS2 = S.OBS2,
            T.TIPOOBS3 = S.TIPOOBS3,
            T.OBS3 = S.OBS3,
            T.TIPOOBS4 = S.TIPOOBS4,
            T.OBS4 = S.OBS4,
            T.TIPOABC = S.TIPOABC,
            T.CODSEGMENTO = S.CODSEGMENTO,
            T.PREFERENCIALSN = S.PREFERENCIALSN,
            T.CLIENTELISTASN = S.CLIENTELISTASN,
            T.AGRUPAMENTO = S.AGRUPAMENTO,
            T.CLIENTE_FORNECEDOR = S.CLIENTE_FORNECEDOR,
            T.DESCRCLIENTE_FORNECEDOR = S.DESCRCLIENTE_FORNECEDOR,
            T.RAZAOSOCIAL = S.RAZAOSOCIAL,
            T.CODIGOERP = S.CODIGOERP,
            T.ETIQUETA = S.ETIQUETA,
            T.EXIGELAUDO = S.EXIGELAUDO,
            T.LAUDO = S.LAUDO,
            T.EMAILLAUDO = S.EMAILLAUDO,
            T.CARTAORCAMENTO = S.CARTAORCAMENTO,
            T.NRETIQUETAS = S.NRETIQUETAS,
            T.IDUNICOREGISTRO = S.IDUNICOREGISTRO,
            T.ACEITAPALETEINCOMPLETO = S.ACEITAPALETEINCOMPLETO,
            T.DESCACEITAPALETEINCOMPLETO = S.DESCACEITAPALETEINCOMPLETO,
            T.IDATENDENTEVENDA = S.IDATENDENTEVENDA,
            T.CONTATOFATURAMENTO = S.CONTATOFATURAMENTO,
            T.IDCLASSFISCAL = S.IDCLASSFISCAL,
            T.DATACRIACAO = S.DATACRIACAO,
            T.USUARIOCRIACAO = S.USUARIOCRIACAO,
            T.DATAULTMODIF = S.DATAULTMODIF,
            T.USUARIOULTMODIF = S.USUARIOULTMODIF,
            T.RAZAOTRAVACOMPOSICAO = S.RAZAOTRAVACOMPOSICAO,
            T.CUSTOFINANCEIROADICIONAL = S.CUSTOFINANCEIROADICIONAL,
            T.CUSTOADICTRANSPORTEPORPALETE = S.CUSTOADICTRANSPORTEPORPALETE,
            T.CUSTOADICTRANSPPORKG_PALETIZ = S.CUSTOADICTRANSPPORKG_PALETIZ,
            T.CUSTOADICTRANSPPORKG_NPALETIZ = S.CUSTOADICTRANSPPORKG_NPALETIZ,
            T.CUSTOADICTRANSPPORM2_PALETIZ = S.CUSTOADICTRANSPPORM2_PALETIZ,
            T.CUSTOADICTRANSPPORM2_NPALETIZ = S.CUSTOADICTRANSPPORM2_NPALETIZ,
            T.CUSTOADICTRANSPPORPECA_PALETIZ = S.CUSTOADICTRANSPPORPECA_PALETIZ,
            T.CUSTOADICTRANSPPORPECANPALETIZ = S.CUSTOADICTRANSPPORPECANPALETIZ,
            T.USOGERALSTR1 = S.USOGERALSTR1,
            T.USOGERALSTR2 = S.USOGERALSTR2,
            T.USOGERALNUM1 = S.USOGERALNUM1,
            T.USOGERALNUM2 = S.USOGERALNUM2,
            T.EXIGECHAPAUNITIZADA = S.EXIGECHAPAUNITIZADA,
            T.EXIGEAGENDAMENTOENTREGAS = S.EXIGEAGENDAMENTOENTREGAS,
            T.CLIENTEPROSPECTO = S.CLIENTEPROSPECTO,
            T.IMPRIMELOGOTIPO = S.IMPRIMELOGOTIPO,
            T.PALETIZADO = S.PALETIZADO,
            T.FACESOPPOSTAS = S.FACESOPPOSTAS,
            T.ESPELHO = S.ESPELHO,
            T.CANTONEIRAS = S.CANTONEIRAS,
            T.FILME = S.FILME,
            T.ORELHASINVERTIDAS = S.ORELHASINVERTIDAS,
            T.PACOTESLARGURA = S.PACOTESLARGURA,
            T.PACOTOSCOMPRIMENTO = S.PACOTOSCOMPRIMENTO,
            T.PACOTESALTURA = S.PACOTESALTURA,
            T.IDPALETE = S.IDPALETE,
            T.EMPILHAMENTOMAXIMO = S.EMPILHAMENTOMAXIMO,
            T.PRESSAODEARQUEAMENTO = S.PRESSAODEARQUEAMENTO,
            T.FITASLARGPALETE = S.FITASLARGPALETE,
            T.FITASCOMMPALETE = S.FITASCOMMPALETE
        WHEN NOT MATCHED THEN INSERT (
            IDCLIENTE, CLIENTE, CODCLIENTE, CODREPRESENTANTE, TOLMAIS, TOLMENOS,
            TIPOOBS1, OBS1, TIPOOBS2, OBS2, TIPOOBS3, OBS3, TIPOOBS4, OBS4,
            TIPOABC, CODSEGMENTO, PREFERENCIALSN, CLIENTELISTASN, AGRUPAMENTO,
            CLIENTE_FORNECEDOR, DESCRCLIENTE_FORNECEDOR, RAZAOSOCIAL, CODIGOERP, ETIQUETA,
            EXIGELAUDO, LAUDO, EMAILLAUDO, CARTAORCAMENTO, NRETIQUETAS, IDUNICOREGISTRO,
            ACEITAPALETEINCOMPLETO, DESCACEITAPALETEINCOMPLETO, IDATENDENTEVENDA,
            CONTATOFATURAMENTO, IDCLASSFISCAL, DATACRIACAO, USUARIOCRIACAO, DATAULTMODIF,
            USUARIOULTMODIF, RAZAOTRAVACOMPOSICAO, CUSTOFINANCEIROADICIONAL,
            CUSTOADICTRANSPORTEPORPALETE, CUSTOADICTRANSPPORKG_PALETIZ,
            CUSTOADICTRANSPPORKG_NPALETIZ, CUSTOADICTRANSPPORM2_PALETIZ,
            CUSTOADICTRANSPPORM2_NPALETIZ, CUSTOADICTRANSPPORPECA_PALETIZ,
            CUSTOADICTRANSPPORPECANPALETIZ, USOGERALSTR1, USOGERALSTR2,
            USOGERALNUM1, USOGERALNUM2, EXIGECHAPAUNITIZADA, EXIGEAGENDAMENTOENTREGAS,
            CLIENTEPROSPECTO, IMPRIMELOGOTIPO, PALETIZADO, FACESOPPOSTAS, ESPELHO,
            CANTONEIRAS, FILME, ORELHASINVERTIDAS, PACOTESLARGURA, PACOTOSCOMPRIMENTO,
            PACOTESALTURA, IDPALETE, EMPILHAMENTOMAXIMO, PRESSAODEARQUEAMENTO,
            FITASLARGPALETE, FITASCOMMPALETE
        ) VALUES (
            S.IDCLIENTE, S.CLIENTE, S.CODCLIENTE, S.CODREPRESENTANTE, S.TOLMAIS, S.TOLMENOS,
            S.TIPOOBS1, S.OBS1, S.TIPOOBS2, S.OBS2, S.TIPOOBS3, S.OBS3, S.TIPOOBS4, S.OBS4,
            S.TIPOABC, S.CODSEGMENTO, S.PREFERENCIALSN, S.CLIENTELISTASN, S.AGRUPAMENTO,
            S.CLIENTE_FORNECEDOR, S.DESCRCLIENTE_FORNECEDOR, S.RAZAOSOCIAL, S.CODIGOERP, S.ETIQUETA,
            S.EXIGELAUDO, S.LAUDO, S.EMAILLAUDO, S.CARTAORCAMENTO, S.NRETIQUETAS, S.IDUNICOREGISTRO,
            S.ACEITAPALETEINCOMPLETO, S.DESCACEITAPALETEINCOMPLETO, S.IDATENDENTEVENDA,
            S.CONTATOFATURAMENTO, S.IDCLASSFISCAL, S.DATACRIACAO, S.USUARIOCRIACAO, S.DATAULTMODIF,
            S.USUARIOULTMODIF, S.RAZAOTRAVACOMPOSICAO, S.CUSTOFINANCEIROADICIONAL,
            S.CUSTOADICTRANSPORTEPORPALETE, S.CUSTOADICTRANSPPORKG_PALETIZ,
            S.CUSTOADICTRANSPPORKG_NPALETIZ, S.CUSTOADICTRANSPPORM2_PALETIZ,
            S.CUSTOADICTRANSPPORM2_NPALETIZ, S.CUSTOADICTRANSPPORPECA_PALETIZ,
            S.CUSTOADICTRANSPPORPECANPALETIZ, S.USOGERALSTR1, S.USOGERALSTR2,
            S.USOGERALNUM1, S.USOGERALNUM2, S.EXIGECHAPAUNITIZADA, S.EXIGEAGENDAMENTOENTREGAS,
            S.CLIENTEPROSPECTO, S.IMPRIMELOGOTIPO, S.PALETIZADO, S.FACESOPPOSTAS, S.ESPELHO,
            S.CANTONEIRAS, S.FILME, S.ORELHASINVERTIDAS, S.PACOTESLARGURA, S.PACOTOSCOMPRIMENTO,
            S.PACOTESALTURA, S.IDPALETE, S.EMPILHAMENTOMAXIMO, S.PRESSAODEARQUEAMENTO,
            S.FITASLARGPALETE, S.FITASCOMMPALETE
        )
    """

    dst = _make_oracle_conn()
    try:
        cur = dst.cursor()
        
        # Configurar inputs específicos para TIMESTAMP
        for param in payload:
            if 'DATACRIACAO' in param and isinstance(param['DATACRIACAO'], datetime):
                # Garantir que temos microssegundos para TIMESTAMP(6)
                if param['DATACRIACAO'].microsecond == 0:
                    # Se não tem microssegundos, adiciona alguns para preencher
                    param['DATACRIACAO'] = param['DATACRIACAO'].replace(microsecond=123456)
            
            if 'DATAULTMODIF' in param and isinstance(param['DATAULTMODIF'], datetime):
                if param['DATAULTMODIF'].microsecond == 0:
                    param['DATAULTMODIF'] = param['DATAULTMODIF'].replace(microsecond=123456)
        
        cur.executemany(merge_sql, payload)
        dst.commit()
        log.info("Oracle <- %s registros mergeados com sucesso.", len(payload))
        
        # Log final para verificação
        if payload:
            sample = payload[0]
            log.info("DATACRIACAO enviada para Oracle: %s", sample.get("DATACRIACAO"))
            log.info("DATAULTMODIF enviada para Oracle: %s", sample.get("DATAULTMODIF"))
            
    except Exception as e:
        log.error("Erro ao fazer MERGE no Oracle: %s", str(e))
        dst.rollback()
        raise
    finally:
        dst.close()

# -----------------
# DAG
# -----------------
with DAG(
    dag_id="etl_clientes",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "sqlserver", "oracle", "clientes"],
    default_args={
        'retries': 2,
    }
):
    PythonOperator(
        task_id="merge_upsert_clientes",
        python_callable=etl_clientes,
    )