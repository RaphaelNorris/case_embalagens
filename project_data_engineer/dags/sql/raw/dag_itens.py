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
# Converters/mapeamentos para ITENS
# -----------------
def _bit_to_char(v: Any) -> str:
    if v is None:
        return "N"
    return "Y" if v in (1, True, "1", "Y", "y") else "N"

def _number_to_int(v: Any) -> int:
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None

def _guid_to_raw16(v: Any):
    if v is None:
        return None
    if isinstance(v, (bytes, bytearray)) and len(v) == 16:
        return bytes(v)
    s = str(v).strip().lower().replace("-", "")
    if len(s) != 32:
        return None
    return binascii.unhexlify(s)

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

def _map_row_to_oracle_itens(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeamento das colunas do SQL Server para Oracle para a tabela ITENS.
    """
    return {
        "ITEM": row.get("Item"),
        "CONJUNTO": row.get("Conjunto"),
        "IDTIPOFT": _number_to_int(row.get("IDTipoFT")),
        "IDTIPOFT2": _number_to_int(row.get("IDTipoFT2")),
        "IDTIPOFT3": _number_to_int(row.get("IDTipoFT3")),
        "IDTIPOFT4": _number_to_int(row.get("IDTipoFT4")),
        "IDTIPOFT5": _number_to_int(row.get("IDTipoFT5")),
        "IDTIPOIPI": _number_to_int(row.get("IDTipoIPI")),
        "IDCLASSFISCAL": _number_to_int(row.get("IDClassFiscal")),
        "IDFAMILIA": _number_to_int(row.get("IDFamilia")),
        "IDAGRUPAMENTO": _number_to_int(row.get("IDAgrupamento")),
        "ESTADOFT_DETEC": _number_to_int(row.get("EstadoFT_Detec")),
        "TEXTOESTADOFT_DETEC": row.get("TextoEstadoFT_Detec"),
        "RAZAOESTADOFT": row.get("RazaoEstadoFT"),
        "STATUSFT": _number_to_int(row.get("StatusFT")),
        "TEXTOSTATUSFT": row.get("TextoStatusFT"),
        "RAZAOSUSP": row.get("RazaoSusp"),
        "VERSAO": _number_to_int(row.get("Versao")),
        "OBSVERSAO": row.get("ObsVersao"),
        "IDCLIENTE": _number_to_int(row.get("IDCliente")),
        "REFERENCIA": row.get("Referencia"),
        "CODIGOREFERENCIA": row.get("CodigoReferencia"),
        "CODIGOEAN": row.get("CodigoEAN"),
        "TIPOABNT": row.get("TipoABNT"),
        "PECASPORUNIDADE": row.get("PecasPorUnidade"),
        "UNIDADESPORCONJUNTO": row.get("UnidadesPorConjunto"),
        "PECASPORCONJUNTO": row.get("PecasPorConjunto"),
        "EXIGELAUDO": _number_to_int(row.get("ExigeLaudo")),
        "GRAMATURA": row.get("Gramatura"),
        "MULLENMINIMO": row.get("MullenMinimo"),
        "CRUSHMINIMO": row.get("CrushMinimo"),
        "COLUNAMINIMO": row.get("ColunaMinimo"),
        "COBBINTMAXIMO": row.get("CobbIntMaximo"),
        "COBBEXTMAXIMO": row.get("CobbExtMaximo"),
        "COBBINT30MAXIMO": row.get("CobbInt30Maximo"),
        "COBBEXT30MAXIMO": row.get("CobbExt30Maximo"),
        "TESTEFISICOADICIONAL1": row.get("TesteFisicoAdicional1"),
        "PAT_INTERNO": row.get("PAT_Interno"),
        "PAT_EXTERNO": row.get("PAT_Externo"),
        "ESPESSURA": row.get("Espessura"),
        "UMIDADE": row.get("Umidade"),
        "COMPRESSAO": row.get("Compressao"),
        "PROFUNDIDADEVINCO": row.get("ProfundidadeVinco"),
        "FORCADEVINCO1": row.get("ForcaDeVinco1"),
        "FORCADEVINCO2": row.get("ForcaDeVinco2"),
        "FORCADEVINCO3": row.get("ForcaDeVinco3"),
        "COMPOSICAO": row.get("Composicao"),
        "FORMATOSIMPLEX": row.get("FormatoSimplex"),
        "LARGURA": row.get("Largura"),
        "REFILOLARGURA": _number_to_int(row.get("RefiloLargura")),
        "COMPRIMENTO": row.get("Comprimento"),
        "REFILOCOMPRIMENTO": _number_to_int(row.get("RefiloComprimento")),
        "MULTLARG": _number_to_int(row.get("MultLarg")),
        "MULTCOMP": _number_to_int(row.get("MultComp")),
        "ARRANJO": row.get("Arranjo"),
        "REFUGOCLIENTE": row.get("RefugoCliente"),
        "VINCOSLARGNORISCADOR": _bit_to_char(row.get("VincosLargNoricador")),
        "VINCOLARG1": row.get("VincoLarg1"),
        "VINCOLARG2": row.get("VincoLarg2"),
        "VINCOLARG3": row.get("VincoLarg3"),
        "VINCOLARG4": row.get("VincoLarg4"),
        "VINCOLARG5": row.get("VincoLarg5"),
        "VINCOLARG6": row.get("VincoLarg6"),
        "VINCOLARG7": row.get("VincoLarg7"),
        "VINCOLARG8": row.get("VincoLarg8"),
        "VINCOLARG9": row.get("VincoLarg9"),
        "VINCOLARG10": row.get("VincoLarg10"),
        "VINCOSCOMPNORISCADOR": _bit_to_char(row.get("VincosCompNoricador")),
        "VINCOCOMP1": row.get("VincoComp1"),
        "VINCOCOMP2": row.get("VincoComp2"),
        "VINCOCOMP3": row.get("VincoComp3"),
        "VINCOCOMP4": row.get("VincoComp4"),
        "VINCOCOMP5": row.get("VincoComp5"),
        "VINCOCOMP6": row.get("VincoComp6"),
        "VINCOCOMP7": row.get("VincoComp7"),
        "VINCOCOMP8": row.get("VincoComp8"),
        "VINCOCOMP9": row.get("VincoComp9"),
        "VINCOCOMP10": row.get("VincoComp10"),
        "TEARTAPE1": _number_to_int(row.get("TearTape1")),
        "TEARTAPE2": _number_to_int(row.get("TearTape2")),
        "TEARTAPE3": _number_to_int(row.get("TearTape3")),
        "TEARTAPE4": _number_to_int(row.get("TearTape4")),
        "LAP": _number_to_int(row.get("Lap")),
        "PROLONGLAP": _number_to_int(row.get("ProlongLap")),
        "LAPNOCOMP": _number_to_int(row.get("LapNoComp")),
        "TEXTO_LAPNOCOMP": row.get("Texto_LapNoComp"),
        "LAPINTERNO": _number_to_int(row.get("LapInterno")),
        "TEXTO_LAPINTERNO": row.get("Texto_LapInterno"),
        "LAPPRIMVINCO": _number_to_int(row.get("LapPrimVinco")),
        "REFILADO": _number_to_int(row.get("Refilado")),
        "REJEITO": _number_to_int(row.get("Rejeito")),
        "REJEITOPECAS": _number_to_int(row.get("RejeitoPecas")),
        "RESINAINTERNA": _number_to_int(row.get("ResinaInterna")),
        "RESINAINTERNASN": _number_to_int(row.get("ResinaInternaSN")),
        "RESINAEXTERNA": _number_to_int(row.get("ResinaExterna")),
        "RESINAEXTERNASN": _number_to_int(row.get("ResinaExternaSN")),
        "ENDURECEDORMIOLO": row.get("EndurecedorMiolo"),
        "ENDURECEDORMIOLOSN": _number_to_int(row.get("EndurecedorMioloSN")),
        "FECHAMENTO": row.get("Fechamento"),
        "GRAMPOS": row.get("Grampos"),
        "AMARRADO": _number_to_int(row.get("Amarrado")),
        "FITILHOSLARGPACOTE": row.get("FitilhosLargPacote"),
        "FITILHOSCOMPPACOTE": row.get("FitilhosCompPacote"),
        "PALETIZADO": _number_to_int(row.get("Paletizado")),
        "PACOTESLARGURA": row.get("PacotesLargura"),
        "PACOTESCOMPRIMENTO": row.get("PacotesComprimento"),
        "PACOTESALTURA": row.get("PacotesAltura"),
        "PECASPORPACOTE": row.get("PecasPorPacote"),
        "PECASPORPALETE": row.get("PecasPorPalete"),
        "PACOTESPORPALETE": row.get("PacotesPorPalete"),
        "UNIDADESPORPALETE": row.get("UnidadesPorPalete"),
        "FITASLARGPALETE": row.get("FitasLargPalete"),
        "FITASCOMPPALETE": row.get("FitasCompPalete"),
        "FACESOPPOSTAS": _number_to_int(row.get("FacesOpostas")),
        "ESPELHO": _number_to_int(row.get("Espelho")),
        "CANTONEIRAS": _number_to_int(row.get("Cantoneiras")),
        "FILME": _number_to_int(row.get("Filme")),
        "ORELHASINVERTIDAS": _number_to_int(row.get("OrelhasInvertidas")),
        "FACA": row.get("Faca"),
        "CODFI": row.get("CodFI"),
        "COR1": row.get("Cor1"),
        "CONSUMOCOR1": row.get("ConsumoCor1"),
        "VISCOSIDADECOR1": row.get("ViscosidadeCor1"),
        "COR2": row.get("Cor2"),
        "CONSUMOCOR2": row.get("ConsumoCor2"),
        "VISCOSIDADECOR2": row.get("ViscosidadeCor2"),
        "COR3": row.get("Cor3"),
        "CONSUMOCOR3": row.get("ConsumoCor3"),
        "VISCOSIDADECOR3": row.get("ViscosidadeCor3"),
        "COR4": row.get("Cor4"),
        "CONSUMOCOR4": row.get("ConsumoCor4"),
        "VISCOSIDADECOR4": row.get("ViscosidadeCor4"),
        "COR5": row.get("Cor5"),
        "CONSUMOCOR5": row.get("ConsumoCor5"),
        "VISCOSIDADECOR5": row.get("ViscosidadeCor5"),
        "COR6": row.get("Cor6"),
        "CONSUMOCOR6": row.get("ConsumoCor6"),
        "VISCOSIDADECOR6": row.get("ViscosidadeCor6"),
        "NRCORES": row.get("NrCores"),
        "IMPCOMREGISTRO": _number_to_int(row.get("ImpComRegistro")),
        "DETALHECV": _number_to_int(row.get("DetalheCV")),
        "TOLMAIS": _number_to_int(row.get("TolMais")),
        "TOLMENOS": _number_to_int(row.get("TolMenos")),
        "TIPOOBS1": row.get("TipoObs1"),
        "OBS1": row.get("Obs1"),
        "TIPOOBS2": row.get("TipoObs2"),
        "OBS2": row.get("Obs2"),
        "TIPOOBS3": row.get("TipoObs3"),
        "OBS3": row.get("Obs3"),
        "TIPOOBS4": row.get("TipoObs4"),
        "OBS4": row.get("Obs4"),
        "TIPOOBS5": row.get("TipoObs5"),
        "OBS5": row.get("Obs5"),
        "TIPOOBS6": row.get("TipoObs6"),
        "OBS6": row.get("Obs6"),
        "TIPOOBS7": row.get("TipoObs7"),
        "OBS7": row.get("Obs7"),
        "TIPOOBS8": row.get("TipoObs8"),
        "OBS8": row.get("Obs8"),
        "LARGURAINTERNA": row.get("LarguraInterna"),
        "COMPRIMENTOINTERNO": row.get("ComprimentoInterno"),
        "ALTURAINTERNA": row.get("AlturaInterna"),
        "LARGPECA": row.get("LargPeca"),
        "COMPPECA": row.get("CompPeca"),
        "DIMADIC1": row.get("DimAdic1"),
        "DIMADIC2": row.get("DimAdic2"),
        "DIMADIC3": row.get("DimAdic3"),
        "DIMADIC4": row.get("DimAdic4"),
        "DIMADIC5": row.get("DimAdic5"),
        "DIMADIC6": row.get("DimAdic6"),
        "CONTRAONDA": _bit_to_char(row.get("ContraOnda")),
        "IMPRIMELOGOTIPO": _number_to_int(row.get("ImprimeLogotipo")),
        "COMISSAODEVENDAS": row.get("ComissaoDeVendas"),
        "USUARIOCRIACAO": _number_to_int(row.get("UsuarioCriacao")),
        "USUARIO": _number_to_int(row.get("Usuario")),
        "PESOADIC": row.get("PesoAdic"),
        "CUSTOUNITADIC": row.get("CustoUnitAdic"),
        "DATAMODIF": _convert_to_timestamp(row.get("DataModif")),
        "DATACRIACAO": _convert_to_timestamp(row.get("DataCriacao")),
        "COMPPACOTE": row.get("CompPacote"),
        "LARGPACOTE": row.get("LargPacote"),
        "ALTURAPACOTE": row.get("AlturaPacote"),
        "COMMPALETEFECHADO": row.get("CompPaleteFechado"),
        "LARGPALETEFECHADO": row.get("LargPaleteFechado"),
        "ALTURAPALETEFECHADO": row.get("AlturaPaleteFechado"),
        "POROSIDADEMINIMO": row.get("PorosidadeMinimo"),
        "PESOCAIXA": row.get("PesoCaixa"),
        "PROJETO": row.get("Projeto"),
        "REFILOONDULADEIRA": row.get("RefiloOnduladeira"),
        "TIPOCUSTOEXTRA": row.get("TipoCustoExtra"),
        "TRAVACOMPOSICAO": _number_to_int(row.get("TravaComposicao")),
        "DESCRTRAVACOMPOSICAO": row.get("DescrTravaComposicao"),
        "PRECO_NEGOCIADO": row.get("Preco_Negociado"),
        "REFILOONDORCAM": row.get("RefiloOndOrcam"),
        "REFILOCOMPORCAM": row.get("RefiloCompOrcam"),
        "GRUPOPALETIZACAO": row.get("GrupoPaletizacao"),
        "PATHFIGURADOLASTRO": row.get("PathFiguraDoLastro"),
        "PATHFIGURADAFT": row.get("PathFiguraDaFT"),
        "PRESSAODEARQUEAMENTO": row.get("PressaoDeArqueamento"),
        "EMPILHAMENTOMAXIMO": row.get("EmpilhamentoMaximo"),
        "IDPALETE": row.get("IDPalete"),
        "REFERENCIAGRUPOPALETIZACAO": row.get("ReferenciaGrupoPaletizacao"),
        "CODIGOERP": row.get("CodigoERP"),
        "IDUNICOREGISTRO": _guid_to_raw16(row.get("IDUnicoRegistro")),
        "FLAGESTOQUEOUTERCEIROS": _number_to_int(row.get("FlagEstoqueOuterceiros")),
        "DESCFLAGESTOQUEOUTERCEIROS": row.get("DescFlagEstoqueOuterceiros"),
        "NRPEDSPILOTO": row.get("NrPedsPiloto"),
        "AREAUTILCEDIDAFACA": row.get("AreaUtilCedidaFaca"),
        "AREABRUTAPECACOMREFILOS": row.get("AreaBrutaPecaComRefilos"),
        "AREABRUTAPECA": row.get("AreaBrutaPeca"),
        "AREALIQUIDAPECA": row.get("AreaLiquidaPeca"),
        "AREABRUTACHAPA": row.get("AreaBrutaChapa"),
        "AREALIQUIDACHAPA": row.get("AreaLiquidaChapa"),
        "VOLUMEPALETEFECHADOM3": row.get("VolumePaleteFechadoM3"),
        "VOLUMEPACOTEFECHADOM3": row.get("VolumePacoteFechadoM3"),
        "IDUSUARIOANALISE": _number_to_int(row.get("IDUsuarioAnalise")),
        "PRECOFERRAMENTAS": row.get("PrecoFerramentas"),
        "QUANTPREVISTA": _number_to_int(row.get("QuantPrevista")),
        "RESUMOCHAPA": row.get("ResumoChapa"),
        "COMPLEMENTOCHAPA": row.get("ComplementoChapa"),
    }

# -----------------
# Tarefa principal para ITENS
# -----------------
def etl_itens(**context):
    # 1) Extrai do SQL Server
    sql = "SELECT * FROM ITENS"
    src_conn = _make_mssql_conn()
    try:
        with src_conn.cursor() as cur:
            cur.execute(sql)
            columns = [column[0] for column in cur.description]
            rows = []
            for row in cur.fetchall():
                rows.append(dict(zip(columns, row)))
        log.info("SQL Server -> %s registros extraídos da tabela ITENS.", len(rows))
        
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
            mapped_row = _map_row_to_oracle_itens(r)
            payload.append(mapped_row)
        except Exception as e:
            log.warning("Erro ao mapear linha: %s. Linha ignorada.", str(e))
            continue

    if not payload:
        log.info("Nenhum dado válido para processar após mapeamento.")
        return

    # 3) MERGE no Oracle
    merge_sql = """
        MERGE INTO ITENS T
        USING (
            SELECT
                :ITEM ITEM, :CONJUNTO CONJUNTO, :IDTIPOFT IDTIPOFT, :IDTIPOFT2 IDTIPOFT2,
                :IDTIPOFT3 IDTIPOFT3, :IDTIPOFT4 IDTIPOFT4, :IDTIPOFT5 IDTIPOFT5,
                :IDTIPOIPI IDTIPOIPI, :IDCLASSFISCAL IDCLASSFISCAL, :IDFAMILIA IDFAMILIA,
                :IDAGRUPAMENTO IDAGRUPAMENTO, :ESTADOFT_DETEC ESTADOFT_DETEC,
                :TEXTOESTADOFT_DETEC TEXTOESTADOFT_DETEC, :RAZAOESTADOFT RAZAOESTADOFT,
                :STATUSFT STATUSFT, :TEXTOSTATUSFT TEXTOSTATUSFT, :RAZAOSUSP RAZAOSUSP,
                :VERSAO VERSAO, :OBSVERSAO OBSVERSAO, :IDCLIENTE IDCLIENTE,
                :REFERENCIA REFERENCIA, :CODIGOREFERENCIA CODIGOREFERENCIA,
                :CODIGOEAN CODIGOEAN, :TIPOABNT TIPOABNT, :PECASPORUNIDADE PECASPORUNIDADE,
                :UNIDADESPORCONJUNTO UNIDADESPORCONJUNTO, :PECASPORCONJUNTO PECASPORCONJUNTO,
                :EXIGELAUDO EXIGELAUDO, :GRAMATURA GRAMATURA, :MULLENMINIMO MULLENMINIMO,
                :CRUSHMINIMO CRUSHMINIMO, :COLUNAMINIMO COLUNAMINIMO, :COBBINTMAXIMO COBBINTMAXIMO,
                :COBBEXTMAXIMO COBBEXTMAXIMO, :COBBINT30MAXIMO COBBINT30MAXIMO,
                :COBBEXT30MAXIMO COBBEXT30MAXIMO, :TESTEFISICOADICIONAL1 TESTEFISICOADICIONAL1,
                :PAT_INTERNO PAT_INTERNO, :PAT_EXTERNO PAT_EXTERNO, :ESPESSURA ESPESSURA,
                :UMIDADE UMIDADE, :COMPRESSAO COMPRESSAO, :PROFUNDIDADEVINCO PROFUNDIDADEVINCO,
                :FORCADEVINCO1 FORCADEVINCO1, :FORCADEVINCO2 FORCADEVINCO2, :FORCADEVINCO3 FORCADEVINCO3,
                :COMPOSICAO COMPOSICAO, :FORMATOSIMPLEX FORMATOSIMPLEX, :LARGURA LARGURA,
                :REFILOLARGURA REFILOLARGURA, :COMPRIMENTO COMPRIMENTO, :REFILOCOMPRIMENTO REFILOCOMPRIMENTO,
                :MULTLARG MULTLARG, :MULTCOMP MULTCOMP, :ARRANJO ARRANJO, :REFUGOCLIENTE REFUGOCLIENTE,
                :VINCOSLARGNORISCADOR VINCOSLARGNORISCADOR, :VINCOLARG1 VINCOLARG1, :VINCOLARG2 VINCOLARG2,
                :VINCOLARG3 VINCOLARG3, :VINCOLARG4 VINCOLARG4, :VINCOLARG5 VINCOLARG5, :VINCOLARG6 VINCOLARG6,
                :VINCOLARG7 VINCOLARG7, :VINCOLARG8 VINCOLARG8, :VINCOLARG9 VINCOLARG9, :VINCOLARG10 VINCOLARG10,
                :VINCOSCOMPNORISCADOR VINCOSCOMPNORISCADOR, :VINCOCOMP1 VINCOCOMP1, :VINCOCOMP2 VINCOCOMP2,
                :VINCOCOMP3 VINCOCOMP3, :VINCOCOMP4 VINCOCOMP4, :VINCOCOMP5 VINCOCOMP5, :VINCOCOMP6 VINCOCOMP6,
                :VINCOCOMP7 VINCOCOMP7, :VINCOCOMP8 VINCOCOMP8, :VINCOCOMP9 VINCOCOMP9, :VINCOCOMP10 VINCOCOMP10,
                :TEARTAPE1 TEARTAPE1, :TEARTAPE2 TEARTAPE2, :TEARTAPE3 TEARTAPE3, :TEARTAPE4 TEARTAPE4,
                :LAP LAP, :PROLONGLAP PROLONGLAP, :LAPNOCOMP LAPNOCOMP, :TEXTO_LAPNOCOMP TEXTO_LAPNOCOMP,
                :LAPINTERNO LAPINTERNO, :TEXTO_LAPINTERNO TEXTO_LAPINTERNO, :LAPPRIMVINCO LAPPRIMVINCO,
                :REFILADO REFILADO, :REJEITO REJEITO, :REJEITOPECAS REJEITOPECAS, :RESINAINTERNA RESINAINTERNA,
                :RESINAINTERNASN RESINAINTERNASN, :RESINAEXTERNA RESINAEXTERNA, :RESINAEXTERNASN RESINAEXTERNASN,
                :ENDURECEDORMIOLO ENDURECEDORMIOLO, :ENDURECEDORMIOLOSN ENDURECEDORMIOLOSN, :FECHAMENTO FECHAMENTO,
                :GRAMPOS GRAMPOS, :AMARRADO AMARRADO, :FITILHOSLARGPACOTE FITILHOSLARGPACOTE,
                :FITILHOSCOMPPACOTE FITILHOSCOMPPACOTE, :PALETIZADO PALETIZADO, :PACOTESLARGURA PACOTESLARGURA,
                :PACOTESCOMPRIMENTO PACOTESCOMPRIMENTO, :PACOTESALTURA PACOTESALTURA, :PECASPORPACOTE PECASPORPACOTE,
                :PECASPORPALETE PECASPORPALETE, :PACOTESPORPALETE PACOTESPORPALETE, :UNIDADESPORPALETE UNIDADESPORPALETE,
                :FITASLARGPALETE FITASLARGPALETE, :FITASCOMPPALETE FITASCOMPPALETE, :FACESOPPOSTAS FACESOPPOSTAS,
                :ESPELHO ESPELHO, :CANTONEIRAS CANTONEIRAS, :FILME FILME, :ORELHASINVERTIDAS ORELHASINVERTIDAS,
                :FACA FACA, :CODFI CODFI, :COR1 COR1, :CONSUMOCOR1 CONSUMOCOR1, :VISCOSIDADECOR1 VISCOSIDADECOR1,
                :COR2 COR2, :CONSUMOCOR2 CONSUMOCOR2, :VISCOSIDADECOR2 VISCOSIDADECOR2, :COR3 COR3,
                :CONSUMOCOR3 CONSUMOCOR3, :VISCOSIDADECOR3 VISCOSIDADECOR3, :COR4 COR4, :CONSUMOCOR4 CONSUMOCOR4,
                :VISCOSIDADECOR4 VISCOSIDADECOR4, :COR5 COR5, :CONSUMOCOR5 CONSUMOCOR5, :VISCOSIDADECOR5 VISCOSIDADECOR5,
                :COR6 COR6, :CONSUMOCOR6 CONSUMOCOR6, :VISCOSIDADECOR6 VISCOSIDADECOR6, :NRCORES NRCORES,
                :IMPCOMREGISTRO IMPCOMREGISTRO, :DETALHECV DETALHECV, :TOLMAIS TOLMAIS, :TOLMENOS TOLMENOS,
                :TIPOOBS1 TIPOOBS1, :OBS1 OBS1, :TIPOOBS2 TIPOOBS2, :OBS2 OBS2, :TIPOOBS3 TIPOOBS3, :OBS3 OBS3,
                :TIPOOBS4 TIPOOBS4, :OBS4 OBS4, :TIPOOBS5 TIPOOBS5, :OBS5 OBS5, :TIPOOBS6 TIPOOBS6, :OBS6 OBS6,
                :TIPOOBS7 TIPOOBS7, :OBS7 OBS7, :TIPOOBS8 TIPOOBS8, :OBS8 OBS8, :LARGURAINTERNA LARGURAINTERNA,
                :COMPRIMENTOINTERNO COMPRIMENTOINTERNO, :ALTURAINTERNA ALTURAINTERNA, :LARGPECA LARGPECA,
                :COMPPECA COMPPECA, :DIMADIC1 DIMADIC1, :DIMADIC2 DIMADIC2, :DIMADIC3 DIMADIC3, :DIMADIC4 DIMADIC4,
                :DIMADIC5 DIMADIC5, :DIMADIC6 DIMADIC6, :CONTRAONDA CONTRAONDA, :IMPRIMELOGOTIPO IMPRIMELOGOTIPO,
                :COMISSAODEVENDAS COMISSAODEVENDAS, :USUARIOCRIACAO USUARIOCRIACAO, :USUARIO USUARIO,
                :PESOADIC PESOADIC, :CUSTOUNITADIC CUSTOUNITADIC, :DATAMODIF DATAMODIF, :DATACRIACAO DATACRIACAO,
                :COMPPACOTE COMPPACOTE, :LARGPACOTE LARGPACOTE, :ALTURAPACOTE ALTURAPACOTE,
                :COMMPALETEFECHADO COMMPALETEFECHADO, :LARGPALETEFECHADO LARGPALETEFECHADO,
                :ALTURAPALETEFECHADO ALTURAPALETEFECHADO, :POROSIDADEMINIMO POROSIDADEMINIMO,
                :PESOCAIXA PESOCAIXA, :PROJETO PROJETO, :REFILOONDULADEIRA REFILOONDULADEIRA,
                :TIPOCUSTOEXTRA TIPOCUSTOEXTRA, :TRAVACOMPOSICAO TRAVACOMPOSICAO,
                :DESCRTRAVACOMPOSICAO DESCRTRAVACOMPOSICAO, :PRECO_NEGOCIADO PRECO_NEGOCIADO,
                :REFILOONDORCAM REFILOONDORCAM, :REFILOCOMPORCAM REFILOCOMPORCAM,
                :GRUPOPALETIZACAO GRUPOPALETIZACAO, :PATHFIGURADOLASTRO PATHFIGURADOLASTRO,
                :PATHFIGURADAFT PATHFIGURADAFT, :PRESSAODEARQUEAMENTO PRESSAODEARQUEAMENTO,
                :EMPILHAMENTOMAXIMO EMPILHAMENTOMAXIMO, :IDPALETE IDPALETE,
                :REFERENCIAGRUPOPALETIZACAO REFERENCIAGRUPOPALETIZACAO, :CODIGOERP CODIGOERP,
                :IDUNICOREGISTRO IDUNICOREGISTRO, :FLAGESTOQUEOUTERCEIROS FLAGESTOQUEOUTERCEIROS,
                :DESCFLAGESTOQUEOUTERCEIROS DESCFLAGESTOQUEOUTERCEIROS, :NRPEDSPILOTO NRPEDSPILOTO,
                :AREAUTILCEDIDAFACA AREAUTILCEDIDAFACA, :AREABRUTAPECACOMREFILOS AREABRUTAPECACOMREFILOS,
                :AREABRUTAPECA AREABRUTAPECA, :AREALIQUIDAPECA AREALIQUIDAPECA, :AREABRUTACHAPA AREABRUTACHAPA,
                :AREALIQUIDACHAPA AREALIQUIDACHAPA, :VOLUMEPALETEFECHADOM3 VOLUMEPALETEFECHADOM3,
                :VOLUMEPACOTEFECHADOM3 VOLUMEPACOTEFECHADOM3, :IDUSUARIOANALISE IDUSUARIOANALISE,
                :PRECOFERRAMENTAS PRECOFERRAMENTAS, :QUANTPREVISTA QUANTPREVISTA, :RESUMOCHAPA RESUMOCHAPA,
                :COMPLEMENTOCHAPA COMPLEMENTOCHAPA
            FROM dual
        ) S
        ON (T.ITEM = S.ITEM AND T.CONJUNTO = S.CONJUNTO)
        WHEN MATCHED THEN UPDATE SET
            T.IDTIPOFT = S.IDTIPOFT, T.IDTIPOFT2 = S.IDTIPOFT2, T.IDTIPOFT3 = S.IDTIPOFT3,
            T.IDTIPOFT4 = S.IDTIPOFT4, T.IDTIPOFT5 = S.IDTIPOFT5, T.IDTIPOIPI = S.IDTIPOIPI,
            T.IDCLASSFISCAL = S.IDCLASSFISCAL, T.IDFAMILIA = S.IDFAMILIA, T.IDAGRUPAMENTO = S.IDAGRUPAMENTO,
            T.ESTADOFT_DETEC = S.ESTADOFT_DETEC, T.TEXTOESTADOFT_DETEC = S.TEXTOESTADOFT_DETEC,
            T.RAZAOESTADOFT = S.RAZAOESTADOFT, T.STATUSFT = S.STATUSFT, T.TEXTOSTATUSFT = S.TEXTOSTATUSFT,
            T.RAZAOSUSP = S.RAZAOSUSP, T.VERSAO = S.VERSAO, T.OBSVERSAO = S.OBSVERSAO,
            T.IDCLIENTE = S.IDCLIENTE, T.REFERENCIA = S.REFERENCIA, T.CODIGOREFERENCIA = S.CODIGOREFERENCIA,
            T.CODIGOEAN = S.CODIGOEAN, T.TIPOABNT = S.TIPOABNT, T.PECASPORUNIDADE = S.PECASPORUNIDADE,
            T.UNIDADESPORCONJUNTO = S.UNIDADESPORCONJUNTO, T.PECASPORCONJUNTO = S.PECASPORCONJUNTO,
            T.EXIGELAUDO = S.EXIGELAUDO, T.GRAMATURA = S.GRAMATURA, T.MULLENMINIMO = S.MULLENMINIMO,
            T.CRUSHMINIMO = S.CRUSHMINIMO, T.COLUNAMINIMO = S.COLUNAMINIMO, T.COBBINTMAXIMO = S.COBBINTMAXIMO,
            T.COBBEXTMAXIMO = S.COBBEXTMAXIMO, T.COBBINT30MAXIMO = S.COBBINT30MAXIMO,
            T.COBBEXT30MAXIMO = S.COBBEXT30MAXIMO, T.TESTEFISICOADICIONAL1 = S.TESTEFISICOADICIONAL1,
            T.PAT_INTERNO = S.PAT_INTERNO, T.PAT_EXTERNO = S.PAT_EXTERNO, T.ESPESSURA = S.ESPESSURA,
            T.UMIDADE = S.UMIDADE, T.COMPRESSAO = S.COMPRESSAO, T.PROFUNDIDADEVINCO = S.PROFUNDIDADEVINCO,
            T.FORCADEVINCO1 = S.FORCADEVINCO1, T.FORCADEVINCO2 = S.FORCADEVINCO2, T.FORCADEVINCO3 = S.FORCADEVINCO3,
            T.COMPOSICAO = S.COMPOSICAO, T.FORMATOSIMPLEX = S.FORMATOSIMPLEX, T.LARGURA = S.LARGURA,
            T.REFILOLARGURA = S.REFILOLARGURA, T.COMPRIMENTO = S.COMPRIMENTO, T.REFILOCOMPRIMENTO = S.REFILOCOMPRIMENTO,
            T.MULTLARG = S.MULTLARG, T.MULTCOMP = S.MULTCOMP, T.ARRANJO = S.ARRANJO, T.REFUGOCLIENTE = S.REFUGOCLIENTE,
            T.VINCOSLARGNORISCADOR = S.VINCOSLARGNORISCADOR, T.VINCOLARG1 = S.VINCOLARG1, T.VINCOLARG2 = S.VINCOLARG2,
            T.VINCOLARG3 = S.VINCOLARG3, T.VINCOLARG4 = S.VINCOLARG4, T.VINCOLARG5 = S.VINCOLARG5, T.VINCOLARG6 = S.VINCOLARG6,
            T.VINCOLARG7 = S.VINCOLARG7, T.VINCOLARG8 = S.VINCOLARG8, T.VINCOLARG9 = S.VINCOLARG9, T.VINCOLARG10 = S.VINCOLARG10,
            T.VINCOSCOMPNORISCADOR = S.VINCOSCOMPNORISCADOR, T.VINCOCOMP1 = S.VINCOCOMP1, T.VINCOCOMP2 = S.VINCOCOMP2,
            T.VINCOCOMP3 = S.VINCOCOMP3, T.VINCOCOMP4 = S.VINCOCOMP4, T.VINCOCOMP5 = S.VINCOCOMP5, T.VINCOCOMP6 = S.VINCOCOMP6,
            T.VINCOCOMP7 = S.VINCOCOMP7, T.VINCOCOMP8 = S.VINCOCOMP8, T.VINCOCOMP9 = S.VINCOCOMP9, T.VINCOCOMP10 = S.VINCOCOMP10,
            T.TEARTAPE1 = S.TEARTAPE1, T.TEARTAPE2 = S.TEARTAPE2, T.TEARTAPE3 = S.TEARTAPE3, T.TEARTAPE4 = S.TEARTAPE4,
            T.LAP = S.LAP, T.PROLONGLAP = S.PROLONGLAP, T.LAPNOCOMP = S.LAPNOCOMP, T.TEXTO_LAPNOCOMP = S.TEXTO_LAPNOCOMP,
            T.LAPINTERNO = S.LAPINTERNO, T.TEXTO_LAPINTERNO = S.TEXTO_LAPINTERNO, T.LAPPRIMVINCO = S.LAPPRIMVINCO,
            T.REFILADO = S.REFILADO, T.REJEITO = S.REJEITO, T.REJEITOPECAS = S.REJEITOPECAS, T.RESINAINTERNA = S.RESINAINTERNA,
            T.RESINAINTERNASN = S.RESINAINTERNASN, T.RESINAEXTERNA = S.RESINAEXTERNA, T.RESINAEXTERNASN = S.RESINAEXTERNASN,
            T.ENDURECEDORMIOLO = S.ENDURECEDORMIOLO, T.ENDURECEDORMIOLOSN = S.ENDURECEDORMIOLOSN, T.FECHAMENTO = S.FECHAMENTO,
            T.GRAMPOS = S.GRAMPOS, T.AMARRADO = S.AMARRADO, T.FITILHOSLARGPACOTE = S.FITILHOSLARGPACOTE,
            T.FITILHOSCOMPPACOTE = S.FITILHOSCOMPPACOTE, T.PALETIZADO = S.PALETIZADO, T.PACOTESLARGURA = S.PACOTESLARGURA,
            T.PACOTESCOMPRIMENTO = S.PACOTESCOMPRIMENTO, T.PACOTESALTURA = S.PACOTESALTURA, T.PECASPORPACOTE = S.PECASPORPACOTE,
            T.PECASPORPALETE = S.PECASPORPALETE, T.PACOTESPORPALETE = S.PACOTESPORPALETE, T.UNIDADESPORPALETE = S.UNIDADESPORPALETE,
            T.FITASLARGPALETE = S.FITASLARGPALETE, T.FITASCOMPPALETE = S.FITASCOMPPALETE, T.FACESOPPOSTAS = S.FACESOPPOSTAS,
            T.ESPELHO = S.ESPELHO, T.CANTONEIRAS = S.CANTONEIRAS, T.FILME = S.FILME, T.ORELHASINVERTIDAS = S.ORELHASINVERTIDAS,
            T.FACA = S.FACA, T.CODFI = S.CODFI, T.COR1 = S.COR1, T.CONSUMOCOR1 = S.CONSUMOCOR1, T.VISCOSIDADECOR1 = S.VISCOSIDADECOR1,
            T.COR2 = S.COR2, T.CONSUMOCOR2 = S.CONSUMOCOR2, T.VISCOSIDADECOR2 = S.VISCOSIDADECOR2, T.COR3 = S.COR3,
            T.CONSUMOCOR3 = S.CONSUMOCOR3, T.VISCOSIDADECOR3 = S.VISCOSIDADECOR3, T.COR4 = S.COR4, T.CONSUMOCOR4 = S.CONSUMOCOR4,
            T.VISCOSIDADECOR4 = S.VISCOSIDADECOR4, T.COR5 = S.COR5, T.CONSUMOCOR5 = S.CONSUMOCOR5, T.VISCOSIDADECOR5 = S.VISCOSIDADECOR5,
            T.COR6 = S.COR6, T.CONSUMOCOR6 = S.CONSUMOCOR6, T.VISCOSIDADECOR6 = S.VISCOSIDADECOR6, T.NRCORES = S.NRCORES,
            T.IMPCOMREGISTRO = S.IMPCOMREGISTRO, T.DETALHECV = S.DETALHECV, T.TOLMAIS = S.TOLMAIS, T.TOLMENOS = S.TOLMENOS,
            T.TIPOOBS1 = S.TIPOOBS1, T.OBS1 = S.OBS1, T.TIPOOBS2 = S.TIPOOBS2, T.OBS2 = S.OBS2, T.TIPOOBS3 = S.TIPOOBS3, T.OBS3 = S.OBS3,
            T.TIPOOBS4 = S.TIPOOBS4, T.OBS4 = S.OBS4, T.TIPOOBS5 = S.TIPOOBS5, T.OBS5 = S.OBS5, T.TIPOOBS6 = S.TIPOOBS6, T.OBS6 = S.OBS6,
            T.TIPOOBS7 = S.TIPOOBS7, T.OBS7 = S.OBS7, T.TIPOOBS8 = S.TIPOOBS8, T.OBS8 = S.OBS8, T.LARGURAINTERNA = S.LARGURAINTERNA,
            T.COMPRIMENTOINTERNO = S.COMPRIMENTOINTERNO, T.ALTURAINTERNA = S.ALTURAINTERNA, T.LARGPECA = S.LARGPECA,
            T.COMPPECA = S.COMPPECA, T.DIMADIC1 = S.DIMADIC1, T.DIMADIC2 = S.DIMADIC2, T.DIMADIC3 = S.DIMADIC3, T.DIMADIC4 = S.DIMADIC4,
            T.DIMADIC5 = S.DIMADIC5, T.DIMADIC6 = S.DIMADIC6, T.CONTRAONDA = S.CONTRAONDA, T.IMPRIMELOGOTIPO = S.IMPRIMELOGOTIPO,
            T.COMISSAODEVENDAS = S.COMISSAODEVENDAS, T.USUARIOCRIACAO = S.USUARIOCRIACAO, T.USUARIO = S.USUARIO,
            T.PESOADIC = S.PESOADIC, T.CUSTOUNITADIC = S.CUSTOUNITADIC, T.DATAMODIF = S.DATAMODIF, T.DATACRIACAO = S.DATACRIACAO,
            T.COMPPACOTE = S.COMPPACOTE, T.LARGPACOTE = S.LARGPACOTE, T.ALTURAPACOTE = S.ALTURAPACOTE,
            T.COMMPALETEFECHADO = S.COMMPALETEFECHADO, T.LARGPALETEFECHADO = S.LARGPALETEFECHADO,
            T.ALTURAPALETEFECHADO = S.ALTURAPALETEFECHADO, T.POROSIDADEMINIMO = S.POROSIDADEMINIMO,
            T.PESOCAIXA = S.PESOCAIXA, T.PROJETO = S.PROJETO, T.REFILOONDULADEIRA = S.REFILOONDULADEIRA,
            T.TIPOCUSTOEXTRA = S.TIPOCUSTOEXTRA, T.TRAVACOMPOSICAO = S.TRAVACOMPOSICAO,
            T.DESCRTRAVACOMPOSICAO = S.DESCRTRAVACOMPOSICAO, T.PRECO_NEGOCIADO = S.PRECO_NEGOCIADO,
            T.REFILOONDORCAM = S.REFILOONDORCAM, T.REFILOCOMPORCAM = S.REFILOCOMPORCAM,
            T.GRUPOPALETIZACAO = S.GRUPOPALETIZACAO, T.PATHFIGURADOLASTRO = S.PATHFIGURADOLASTRO,
            T.PATHFIGURADAFT = S.PATHFIGURADAFT, T.PRESSAODEARQUEAMENTO = S.PRESSAODEARQUEAMENTO,
            T.EMPILHAMENTOMAXIMO = S.EMPILHAMENTOMAXIMO, T.IDPALETE = S.IDPALETE,
            T.REFERENCIAGRUPOPALETIZACAO = S.REFERENCIAGRUPOPALETIZACAO, T.CODIGOERP = S.CODIGOERP,
            T.IDUNICOREGISTRO = S.IDUNICOREGISTRO, T.FLAGESTOQUEOUTERCEIROS = S.FLAGESTOQUEOUTERCEIROS,
            T.DESCFLAGESTOQUEOUTERCEIROS = S.DESCFLAGESTOQUEOUTERCEIROS, T.NRPEDSPILOTO = S.NRPEDSPILOTO,
            T.AREAUTILCEDIDAFACA = S.AREAUTILCEDIDAFACA, T.AREABRUTAPECACOMREFILOS = S.AREABRUTAPECACOMREFILOS,
            T.AREABRUTAPECA = S.AREABRUTAPECA, T.AREALIQUIDAPECA = S.AREALIQUIDAPECA, T.AREABRUTACHAPA = S.AREABRUTACHAPA,
            T.AREALIQUIDACHAPA = S.AREALIQUIDACHAPA, T.VOLUMEPALETEFECHADOM3 = S.VOLUMEPALETEFECHADOM3,
            T.VOLUMEPACOTEFECHADOM3 = S.VOLUMEPACOTEFECHADOM3, T.IDUSUARIOANALISE = S.IDUSUARIOANALISE,
            T.PRECOFERRAMENTAS = S.PRECOFERRAMENTAS, T.QUANTPREVISTA = S.QUANTPREVISTA, T.RESUMOCHAPA = S.RESUMOCHAPA,
            T.COMPLEMENTOCHAPA = S.COMPLEMENTOCHAPA
        WHEN NOT MATCHED THEN INSERT (
            ITEM, CONJUNTO, IDTIPOFT, IDTIPOFT2, IDTIPOFT3, IDTIPOFT4, IDTIPOFT5, IDTIPOIPI, IDCLASSFISCAL,
            IDFAMILIA, IDAGRUPAMENTO, ESTADOFT_DETEC, TEXTOESTADOFT_DETEC, RAZAOESTADOFT, STATUSFT, TEXTOSTATUSFT,
            RAZAOSUSP, VERSAO, OBSVERSAO, IDCLIENTE, REFERENCIA, CODIGOREFERENCIA, CODIGOEAN, TIPOABNT,
            PECASPORUNIDADE, UNIDADESPORCONJUNTO, PECASPORCONJUNTO, EXIGELAUDO, GRAMATURA, MULLENMINIMO,
            CRUSHMINIMO, COLUNAMINIMO, COBBINTMAXIMO, COBBEXTMAXIMO, COBBINT30MAXIMO, COBBEXT30MAXIMO,
            TESTEFISICOADICIONAL1, PAT_INTERNO, PAT_EXTERNO, ESPESSURA, UMIDADE, COMPRESSAO, PROFUNDIDADEVINCO,
            FORCADEVINCO1, FORCADEVINCO2, FORCADEVINCO3, COMPOSICAO, FORMATOSIMPLEX, LARGURA, REFILOLARGURA,
            COMPRIMENTO, REFILOCOMPRIMENTO, MULTLARG, MULTCOMP, ARRANJO, REFUGOCLIENTE, VINCOSLARGNORISCADOR,
            VINCOLARG1, VINCOLARG2, VINCOLARG3, VINCOLARG4, VINCOLARG5, VINCOLARG6, VINCOLARG7, VINCOLARG8,
            VINCOLARG9, VINCOLARG10, VINCOSCOMPNORISCADOR, VINCOCOMP1, VINCOCOMP2, VINCOCOMP3, VINCOCOMP4,
            VINCOCOMP5, VINCOCOMP6, VINCOCOMP7, VINCOCOMP8, VINCOCOMP9, VINCOCOMP10, TEARTAPE1, TEARTAPE2,
            TEARTAPE3, TEARTAPE4, LAP, PROLONGLAP, LAPNOCOMP, TEXTO_LAPNOCOMP, LAPINTERNO, TEXTO_LAPINTERNO,
            LAPPRIMVINCO, REFILADO, REJEITO, REJEITOPECAS, RESINAINTERNA, RESINAINTERNASN, RESINAEXTERNA,
            RESINAEXTERNASN, ENDURECEDORMIOLO, ENDURECEDORMIOLOSN, FECHAMENTO, GRAMPOS, AMARRADO,
            FITILHOSLARGPACOTE, FITILHOSCOMPPACOTE, PALETIZADO, PACOTESLARGURA, PACOTESCOMPRIMENTO, PACOTESALTURA,
            PECASPORPACOTE, PECASPORPALETE, PACOTESPORPALETE, UNIDADESPORPALETE, FITASLARGPALETE, FITASCOMPPALETE,
            FACESOPPOSTAS, ESPELHO, CANTONEIRAS, FILME, ORELHASINVERTIDAS, FACA, CODFI, COR1, CONSUMOCOR1,
            VISCOSIDADECOR1, COR2, CONSUMOCOR2, VISCOSIDADECOR2, COR3, CONSUMOCOR3, VISCOSIDADECOR3, COR4,
            CONSUMOCOR4, VISCOSIDADECOR4, COR5, CONSUMOCOR5, VISCOSIDADECOR5, COR6, CONSUMOCOR6, VISCOSIDADECOR6,
            NRCORES, IMPCOMREGISTRO, DETALHECV, TOLMAIS, TOLMENOS, TIPOOBS1, OBS1, TIPOOBS2, OBS2, TIPOOBS3, OBS3,
            TIPOOBS4, OBS4, TIPOOBS5, OBS5, TIPOOBS6, OBS6, TIPOOBS7, OBS7, TIPOOBS8, OBS8, LARGURAINTERNA,
            COMPRIMENTOINTERNO, ALTURAINTERNA, LARGPECA, COMPPECA, DIMADIC1, DIMADIC2, DIMADIC3, DIMADIC4,
            DIMADIC5, DIMADIC6, CONTRAONDA, IMPRIMELOGOTIPO, COMISSAODEVENDAS, USUARIOCRIACAO, USUARIO,
            PESOADIC, CUSTOUNITADIC, DATAMODIF, DATACRIACAO, COMPPACOTE, LARGPACOTE, ALTURAPACOTE,
            COMMPALETEFECHADO, LARGPALETEFECHADO, ALTURAPALETEFECHADO, POROSIDADEMINIMO, PESOCAIXA, PROJETO,
            REFILOONDULADEIRA, TIPOCUSTOEXTRA, TRAVACOMPOSICAO, DESCRTRAVACOMPOSICAO, PRECO_NEGOCIADO,
            REFILOONDORCAM, REFILOCOMPORCAM, GRUPOPALETIZACAO, PATHFIGURADOLASTRO, PATHFIGURADAFT,
            PRESSAODEARQUEAMENTO, EMPILHAMENTOMAXIMO, IDPALETE, REFERENCIAGRUPOPALETIZACAO, CODIGOERP,
            IDUNICOREGISTRO, FLAGESTOQUEOUTERCEIROS, DESCFLAGESTOQUEOUTERCEIROS, NRPEDSPILOTO, AREAUTILCEDIDAFACA,
            AREABRUTAPECACOMREFILOS, AREABRUTAPECA, AREALIQUIDAPECA, AREABRUTACHAPA, AREALIQUIDACHAPA,
            VOLUMEPALETEFECHADOM3, VOLUMEPACOTEFECHADOM3, IDUSUARIOANALISE, PRECOFERRAMENTAS, QUANTPREVISTA,
            RESUMOCHAPA, COMPLEMENTOCHAPA
        ) VALUES (
            S.ITEM, S.CONJUNTO, S.IDTIPOFT, S.IDTIPOFT2, S.IDTIPOFT3, S.IDTIPOFT4, S.IDTIPOFT5, S.IDTIPOIPI, S.IDCLASSFISCAL,
            S.IDFAMILIA, S.IDAGRUPAMENTO, S.ESTADOFT_DETEC, S.TEXTOESTADOFT_DETEC, S.RAZAOESTADOFT, S.STATUSFT, S.TEXTOSTATUSFT,
            S.RAZAOSUSP, S.VERSAO, S.OBSVERSAO, S.IDCLIENTE, S.REFERENCIA, S.CODIGOREFERENCIA, S.CODIGOEAN, S.TIPOABNT,
            S.PECASPORUNIDADE, S.UNIDADESPORCONJUNTO, S.PECASPORCONJUNTO, S.EXIGELAUDO, S.GRAMATURA, S.MULLENMINIMO,
            S.CRUSHMINIMO, S.COLUNAMINIMO, S.COBBINTMAXIMO, S.COBBEXTMAXIMO, S.COBBINT30MAXIMO, S.COBBEXT30MAXIMO,
            S.TESTEFISICOADICIONAL1, S.PAT_INTERNO, S.PAT_EXTERNO, S.ESPESSURA, S.UMIDADE, S.COMPRESSAO, S.PROFUNDIDADEVINCO,
            S.FORCADEVINCO1, S.FORCADEVINCO2, S.FORCADEVINCO3, S.COMPOSICAO, S.FORMATOSIMPLEX, S.LARGURA, S.REFILOLARGURA,
            S.COMPRIMENTO, S.REFILOCOMPRIMENTO, S.MULTLARG, S.MULTCOMP, S.ARRANJO, S.REFUGOCLIENTE, S.VINCOSLARGNORISCADOR,
            S.VINCOLARG1, S.VINCOLARG2, S.VINCOLARG3, S.VINCOLARG4, S.VINCOLARG5, S.VINCOLARG6, S.VINCOLARG7, S.VINCOLARG8,
            S.VINCOLARG9, S.VINCOLARG10, S.VINCOSCOMPNORISCADOR, S.VINCOCOMP1, S.VINCOCOMP2, S.VINCOCOMP3, S.VINCOCOMP4,
            S.VINCOCOMP5, S.VINCOCOMP6, S.VINCOCOMP7, S.VINCOCOMP8, S.VINCOCOMP9, S.VINCOCOMP10, S.TEARTAPE1, S.TEARTAPE2,
            S.TEARTAPE3, S.TEARTAPE4, S.LAP, S.PROLONGLAP, S.LAPNOCOMP, S.TEXTO_LAPNOCOMP, S.LAPINTERNO, S.TEXTO_LAPINTERNO,
            S.LAPPRIMVINCO, S.REFILADO, S.REJEITO, S.REJEITOPECAS, S.RESINAINTERNA, S.RESINAINTERNASN, S.RESINAEXTERNA,
            S.RESINAEXTERNASN, S.ENDURECEDORMIOLO, S.ENDURECEDORMIOLOSN, S.FECHAMENTO, S.GRAMPOS, S.AMARRADO,
            S.FITILHOSLARGPACOTE, S.FITILHOSCOMPPACOTE, S.PALETIZADO, S.PACOTESLARGURA, S.PACOTESCOMPRIMENTO, S.PACOTESALTURA,
            S.PECASPORPACOTE, S.PECASPORPALETE, S.PACOTESPORPALETE, S.UNIDADESPORPALETE, S.FITASLARGPALETE, S.FITASCOMPPALETE,
            S.FACESOPPOSTAS, S.ESPELHO, S.CANTONEIRAS, S.FILME, S.ORELHASINVERTIDAS, S.FACA, S.CODFI, S.COR1, S.CONSUMOCOR1,
            S.VISCOSIDADECOR1, S.COR2, S.CONSUMOCOR2, S.VISCOSIDADECOR2, S.COR3, S.CONSUMOCOR3, S.VISCOSIDADECOR3, S.COR4,
            S.CONSUMOCOR4, S.VISCOSIDADECOR4, S.COR5, S.CONSUMOCOR5, S.VISCOSIDADECOR5, S.COR6, S.CONSUMOCOR6, S.VISCOSIDADECOR6,
            S.NRCORES, S.IMPCOMREGISTRO, S.DETALHECV, S.TOLMAIS, S.TOLMENOS, S.TIPOOBS1, S.OBS1, S.TIPOOBS2, S.OBS2, S.TIPOOBS3, S.OBS3,
            S.TIPOOBS4, S.OBS4, S.TIPOOBS5, S.OBS5, S.TIPOOBS6, S.OBS6, S.TIPOOBS7, S.OBS7, S.TIPOOBS8, S.OBS8, S.LARGURAINTERNA,
            S.COMPRIMENTOINTERNO, S.ALTURAINTERNA, S.LARGPECA, S.COMPPECA, S.DIMADIC1, S.DIMADIC2, S.DIMADIC3, S.DIMADIC4,
            S.DIMADIC5, S.DIMADIC6, S.CONTRAONDA, S.IMPRIMELOGOTIPO, S.COMISSAODEVENDAS, S.USUARIOCRIACAO, S.USUARIO,
            S.PESOADIC, S.CUSTOUNITADIC, S.DATAMODIF, S.DATACRIACAO, S.COMPPACOTE, S.LARGPACOTE, S.ALTURAPACOTE,
            S.COMMPALETEFECHADO, S.LARGPALETEFECHADO, S.ALTURAPALETEFECHADO, S.POROSIDADEMINIMO, S.PESOCAIXA, S.PROJETO,
            S.REFILOONDULADEIRA, S.TIPOCUSTOEXTRA, S.TRAVACOMPOSICAO, S.DESCRTRAVACOMPOSICAO, S.PRECO_NEGOCIADO,
            S.REFILOONDORCAM, S.REFILOCOMPORCAM, S.GRUPOPALETIZACAO, S.PATHFIGURADOLASTRO, S.PATHFIGURADAFT,
            S.PRESSAODEARQUEAMENTO, S.EMPILHAMENTOMAXIMO, S.IDPALETE, S.REFERENCIAGRUPOPALETIZACAO, S.CODIGOERP,
            S.IDUNICOREGISTRO, S.FLAGESTOQUEOUTERCEIROS, S.DESCFLAGESTOQUEOUTERCEIROS, S.NRPEDSPILOTO, S.AREAUTILCEDIDAFACA,
            S.AREABRUTAPECACOMREFILOS, S.AREABRUTAPECA, S.AREALIQUIDAPECA, S.AREABRUTACHAPA, S.AREALIQUIDACHAPA,
            S.VOLUMEPALETEFECHADOM3, S.VOLUMEPACOTEFECHADOM3, S.IDUSUARIOANALISE, S.PRECOFERRAMENTAS, S.QUANTPREVISTA,
            S.RESUMOCHAPA, S.COMPLEMENTOCHAPA
        )
    """

    dst = _make_oracle_conn()
    try:
        cur = dst.cursor()
        
        # Configurar inputs específicos para TIMESTAMP
        for param in payload:
            for date_field in ['DATAMODIF', 'DATACRIACAO']:
                if date_field in param and isinstance(param[date_field], datetime):
                    if param[date_field].microsecond == 0:
                        param[date_field] = param[date_field].replace(microsecond=123456)
        
        cur.executemany(merge_sql, payload)
        dst.commit()
        log.info("Oracle <- %s registros mergeados com sucesso na tabela ITENS.", len(payload))
            
    except Exception as e:
        log.error("Erro ao fazer MERGE no Oracle: %s", str(e))
        dst.rollback()
        raise
    finally:
        dst.close()

# -----------------
# DAG para ITENS
# -----------------
with DAG(
    dag_id="etl_itens",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl","sqlserver","oracle","itens"],
):
    merge_upsert_itens = PythonOperator(
        task_id="merge_upsert_itens",
        python_callable=etl_itens,
    )