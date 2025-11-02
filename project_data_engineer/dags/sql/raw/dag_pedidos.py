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
# Converters/mapeamentos para PEDIDOS
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
            log.warning("Nao foi possivel converter data '%s': %s", value, str(e))
            return None
    
    # Se for outro tipo (date, etc), converte para datetime
    try:
        return datetime.combine(value, datetime.min.time())
    except Exception:
        return None

def _map_row_to_oracle_pedidos(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeamento das colunas do SQL Server para Oracle para a tabela PEDIDOS.
    """
    return {
        "IDPEDIDOS": _number_to_int(row.get("IDPedidos")),
        "PEDIDO": row.get("Pedido"),
        "ITEM": row.get("Item"),
        "ITEMPEDIDO": row.get("ItemPedido"),
        "IDPEDVENDA": _number_to_int(row.get("IDPedVenda")),
        "IDITEMPEDVENDA": _number_to_int(row.get("IDItemPedVenda")),
        "STATUSPEDIDO": _number_to_int(row.get("StatusPedido")),
        "DESCRSTATUSPEDIDO": row.get("DescrStatusPedido"),
        "SUSPENSO": _number_to_int(row.get("Suspenso")),
        "SUSPOUCANCEL": row.get("SuspOuCancel"),
        "VERSAO": _number_to_int(row.get("Versao")),
        "IDCLIENTE": _number_to_int(row.get("IDCliente")),
        "IDLOJA": _number_to_int(row.get("IDLoja")),
        "IDLOCALENTREGA": _number_to_int(row.get("IDLocalEntrega")),
        "IDLOCALCOBRANCA": _number_to_int(row.get("IDLocalCobranca")),
        "REFERENCIA": row.get("Referencia"),
        "CODIGOREFERENCIA": row.get("CodigoReferencia"),
        "CODIGOEAN": row.get("CodigoEAN"),
        "TIPOABNT": row.get("TipoABNT"),
        "IDTIPOFT": _number_to_int(row.get("IDTipoFT")),
        "IDTIPOFT2": _number_to_int(row.get("IDTipoFT2")),
        "IDTIPOFT3": _number_to_int(row.get("IDTipoFT3")),
        "IDTIPOFT4": _number_to_int(row.get("IDTipoFT4")),
        "IDTIPOFT5": _number_to_int(row.get("IDTipoFT5")),
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
        "CHAPA": _number_to_int(row.get("Chapa")),
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
        "PESOPECA": row.get("PesoPeca"),
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
        "LAPINTERNO": _number_to_int(row.get("LapInterno")),
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
        "DESCRPALETIZADO": row.get("DescrPaletizado"),
        "PACOTESLARGURA": row.get("PacotesLargura"),
        "PACOTESCOMPRIMENTO": row.get("PacotesComprimento"),
        "PACOTESALTURA": row.get("PacotesAltura"),
        "PECASPORPACOTE": row.get("PecasPorPacote"),
        "PECASPORPALETE": row.get("PecasPorPalete"),
        "UNIDADESPORPALETE": row.get("UnidadesPorPalete"),
        "PACOTESPORPALETE": row.get("PacotesPorPalete"),
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
        "CONTRAONDA": _bit_to_char(row.get("ContraOnda")),
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
        "TIPOOBS9": row.get("TipoObs9"),
        "OBS9": row.get("Obs9"),
        "DATAENTREGA1": _convert_to_timestamp(row.get("DataEntrega1")),
        "DATAENTREGA2": _convert_to_timestamp(row.get("DataEntrega2")),
        "QUANTIDADEPEDIDA": _number_to_int(row.get("QuantidadePedida")),
        "QUANTIDADEPEDIDAMIN": _number_to_int(row.get("QuantidadePedidaMin")),
        "QUANTIDADEPEDIDAMAX": _number_to_int(row.get("QuantidadePedidaMax")),
        "TIPOENTREGA": _number_to_int(row.get("TipoEntrega")),
        "DESCTIPOENTREGA": row.get("DescTipoEntrega"),
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
        "PRECOVENDA": row.get("PrecoVenda"),
        "CUSTOUNITTRANSP": row.get("CustoUnitTransp"),
        "CUSTOUNITVAR": row.get("CustoUnitVar"),
        "CUSTOUNITFIXO": row.get("CustoUnitFixo"),
        "RESULTOPERACIONAL": row.get("ResultOperacional"),
        "MARGEMCONTRHORA": row.get("MargemContrHora"),
        "RECEITALIQUIDA": row.get("ReceitaLiquida"),
        "VENDALIQUIDA": row.get("VendaLiquida"),
        "MARGEMCONTR": row.get("MargemContr"),
        "PESOADIC": row.get("PesoAdic"),
        "CUSTOUNITADIC": row.get("CustoUnitAdic"),
        "REGIAOORIGEM": row.get("RegiaoOrigem"),
        "DISTANCIA": _number_to_int(row.get("Distancia")),
        "FRETEINCLUSO": _number_to_int(row.get("FreteIncluso")),
        "CONDICAODEPAGAMENTO": row.get("CondicaoDePagamento"),
        "NRDECARROS": _number_to_int(row.get("NrDeCarros")),
        "CUSTOEXTRAFRETE": row.get("CustoExtraFrete"),
        "PRECOFRETE": row.get("PrecoFrete"),
        "PRECOFERRAMENTAS": row.get("PrecoFerramentas"),
        "QUANTPREVISTA": _number_to_int(row.get("QuantPrevista")),
        "DATACRIACAO": _convert_to_timestamp(row.get("DataCriacao")),
        "DATAENTREGAORIGINAL": _convert_to_timestamp(row.get("DataEntregaOriginal")),
        "NIVELURGENCIA": row.get("NivelUrgencia"),
        "DATAULTIMAALTERACAOFT": _convert_to_timestamp(row.get("DataUltimaAlteracaoFT")),
        "FLAGESTOQUEOUTERCEIROS": _number_to_int(row.get("FlagEstoqueOuterceiros")),
        "DESCFLAGESTOQUEOUTERCEIROS": row.get("DescFlagEstoqueOuterceiros"),
        "ADICIONAL1": row.get("Adicional1"),
        "POSSIVELDATAENTREGA": _convert_to_timestamp(row.get("PossivelDataEntrega")),
        "TIPODOPEDIDO": _number_to_int(row.get("TipoDoPedido")),
        "DESCRTIPODOPEDIDO": row.get("DescTipoDoPedido"),
        "TEMPOEXPEDVIAGEM": row.get("TempoExpedViagem"),
        "IMPRIMELOGOTIPO": _number_to_int(row.get("ImprimeLogotipo")),
        "COMISSAODEVENDAS": row.get("ComissaoDeVendas"),
        "VERSAODECUSTO": _number_to_int(row.get("VersaoDeCusto")),
        "COMPPACOTE": row.get("CompPacote"),
        "LARGPACOTE": row.get("LargPacote"),
        "ALTURAPACOTE": row.get("AlturaPacote"),
        "COMPPALETEFECHADO": row.get("CompPaleteFechado"),
        "LARGPALETEFECHADO": row.get("LargPaleteFechado"),
        "ALTURAPALETEFECHADO": row.get("AlturaPaleteFechado"),
        "POROSIDADEMINIMO": row.get("PorosidadeMinimo"),
        "PESOCAIXA": row.get("PesoCaixa"),
        "REFILOONDULADERA": row.get("RefiloOnduladera"),
        "TIPOCUSTOEXTRA": row.get("TipoCustoExtra"),
        "PEDCLIENTE": row.get("PedCliente"),
        "ITEMPEDCLIENTE": row.get("ItemPedCliente"),
        "TIPOCAMINHAO": row.get("TipoCaminhao"),
        "CONJUNTO": row.get("Conjunto"),
        "TRAVACOMPOSICAO": _number_to_int(row.get("TravaComposicao")),
        "DESCRTRAVACOMPOSICAO": row.get("DescrTravaComposicao"),
        "DATAPROMESSA": _convert_to_timestamp(row.get("DataPromessa")),
        "PRECORELACAO": row.get("PrecoRelacao"),
        "PATHFIGURADOLASTRO": row.get("PathFiguraDoLastro"),
        "PATHFIGURADAFT": row.get("PathFiguraDaFT"),
        "PRESSAODEARQUEAMENTO": row.get("PressaoDeArqueamento"),
        "EMPILHAMENTOMAXIMO": row.get("EmpilhamentoMaximo"),
        "GRUPOPALETIZACAO": row.get("GrupoPaletizacao"),
        "LIBERADOPROGEXPED": _number_to_int(row.get("LiberadoProgExped")),
        "IDPALETE": row.get("IDPalete"),
        "REFERENCIAGRUPOPALETIZACAO": row.get("ReferenciaGrupoPaletizacao"),
        "LOTEPILOTO": _number_to_int(row.get("LotePiloto")),
        "PEDIDO_ERP": row.get("Pedido_ERP"),
        "ITEM_ERP": row.get("Item_ERP"),
        "PRODUTO_ERP": row.get("Produto_ERP"),
        "DATACRIACAOREGISTRO": _convert_to_timestamp(row.get("DataCriacaoRegistro")),
        "IDUNICOREGISTRO": _guid_to_raw16(row.get("IDUnicoRegistro")),
        "OBSALTERACOES": row.get("ObsAlteracoes"),
        "IDUSUARIOULTMODIF": _number_to_int(row.get("IDUsuarioUltModif")),
        "ULTMODIFICACAO": _convert_to_timestamp(row.get("UltModificacao")),
        "ORCAMENTO": _number_to_int(row.get("Orcamento")),
        "ITEMORCAMENTO": row.get("ItemOrcamento"),
        "CODREPRESENTANTE": _number_to_int(row.get("CodRepresentante")),
        "CODSEGMENTO": row.get("CodSegmento"),
        "AREAUTILCEDIDAFACA": row.get("AreaUtilCedidaFaca"),
        "AREABRUTAPECACOMREFILOS": row.get("AreaBrutaPecaComRefilos"),
        "AREABRUTAPECA": row.get("AreaBrutaPeca"),
        "AREALIQUIDAPECA": row.get("AreaLiquidaPeca"),
        "AREABRUTACHAPA": row.get("AreaBrutaChapa"),
        "AREALIQUIDACHAPA": row.get("AreaLiquidaChapa"),
        "VOLUMEPALETEFECHADOM3": row.get("VolumePaleteFechadoM3"),
        "VOLUMEPACOTEFECHADOM3": row.get("VolumePacoteFechadoM3"),
        "VOLUMEFECHADOPEDIDO": row.get("VolumeFechadoPedido"),
        "ORIGEMPEDIDO": _number_to_int(row.get("OrigemPedido")),
        "DESCORIGEMPEDIDO": row.get("DescOrigemPedido"),
        "TIPOGERACAOPED": _number_to_int(row.get("TipoGeracaoPed")),
        "DESCTIPOGERACAOPED": row.get("DescTipoGeracaoPed"),
        "IDFILIALEXPEDICAO": _number_to_int(row.get("IDFilialExpedicao")),
        "QTDIMPRESSOES": _number_to_int(row.get("QtdImpressoes")),
        "DATAHORAPRIMEIRAIMPRESSAO": _convert_to_timestamp(row.get("DataHoraPrimeiraImpressao")),
        "IDUSUARIOPRIMEIRAIMPRESSAO": _number_to_int(row.get("IDUsuarioPrimeiraImpressao")),
        "DATAHORAULTIMAIMPRESSAO": _convert_to_timestamp(row.get("DataHoraUltimaImpressao")),
        "IDUSUARIOULTIMAIMPRESSAO": _number_to_int(row.get("IDUsuarioUltimaImpressao")),
        "CHAVE_CHAPA": row.get("Chave_Chapa"),
    }

# -----------------
# Tarefa principal para PEDIDOS
# -----------------

def etl_pedidos(**context):
    # CONFIGURACAO PARA TESTE: APENAS 2 LOTES
    # Para executar todos os lotes, comente a linha abaixo e 
    # modifique o while para: while True:
    #max_batches = 5
    
    # Configuracao de paginacao
    page_size = 20000
    offset = 0
    total_processed = 0
    batch_count = 0
    
    # 1) TRUNCATE na tabela de destino antes da carga
    log.info("Oracle -> Executando TRUNCATE na tabela PEDIDOS...")
    dst_conn = _make_oracle_conn()
    try:
        with dst_conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE PEDIDOS")
        dst_conn.commit()
        log.info("Oracle -> TRUNCATE executado com sucesso na tabela PEDIDOS.")
    except Exception as e:
        log.error("Erro ao executar TRUNCATE no Oracle: %s", str(e))
        dst_conn.rollback()
        raise
    finally:
        dst_conn.close()

    while True: #batch_count < max_batches:  # Modificar para 'while True:' para execucao completa

        # Query com paginacao - usando IDPEDIDOS como chave de ordenacao
        sql = f"""
            SELECT * FROM PEDIDOS 
            ORDER BY IDPEDIDOS
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
            
            log.info("SQL Server -> Pagina %s: %s registros extraidos da tabela PEDIDOS.", 
                    batch_count + 1, len(rows))

            if not rows:
                log.info("Todas as paginas processadas. Total: %s registros.", total_processed)
                break

            # 2) Mapeia para o layout do Oracle
            payload: List[Dict[str, Any]] = []
            for r in rows:
                try:
                    mapped_row = _map_row_to_oracle_pedidos(r)
                    payload.append(mapped_row)
                except Exception as e:
                    log.warning("Erro ao mapear linha: %s. Linha ignorada.", str(e))
                    continue

            if payload:
                # 3) Processa o lote atual (INSERT no Oracle)
                _process_batch_pedidos(payload, batch_count + 1)
                total_processed += len(payload)
                log.info("Pagina %s processada: %s registros validos (total acumulado: %s)", 
                        batch_count + 1, len(payload), total_processed)
            else:
                log.info("Pagina %s sem registros validos, pulando.", batch_count + 1)

            # Prepara proxima pagina
            batch_count += 1
            offset += page_size
            
            # Limpa memoria
            del rows
            del payload

        except Exception as e:
            log.error("Erro ao extrair dados do SQL Server (pagina %s): %s", batch_count + 1, str(e))
            raise
        finally:
            src_conn.close()

    if total_processed == 0:
        log.info("Nenhum dado valido para processar.")
        return

    log.info("ETL concluida: %s registros processados com sucesso.", total_processed)


def _process_batch_pedidos(payload, batch_number):
    """Processa um lote de registros no Oracle com INSERT direto"""
    insert_sql = """
        INSERT INTO PEDIDOS (
            IDPEDIDOS, PEDIDO, ITEM, ITEMPEDIDO, IDPEDVENDA, IDITEMPEDVENDA, STATUSPEDIDO,
            DESCRSTATUSPEDIDO, SUSPENSO, SUSPOUCANCEL, VERSAO, IDCLIENTE, IDLOJA, IDLOCALENTREGA,
            IDLOCALCOBRANCA, REFERENCIA, CODIGOREFERENCIA, CODIGOEAN, TIPOABNT, IDTIPOFT, IDTIPOFT2,
            IDTIPOFT3, IDTIPOFT4, IDTIPOFT5, PECASPORUNIDADE, UNIDADESPORCONJUNTO, PECASPORCONJUNTO,
            EXIGELAUDO, GRAMATURA, MULLENMINIMO, CRUSHMINIMO, COLUNAMINIMO, COBBINTMAXIMO, COBBEXTMAXIMO,
            COBBINT30MAXIMO, COBBEXT30MAXIMO, TESTEFISICOADICIONAL1, PAT_INTERNO, PAT_EXTERNO, ESPESSURA,
            UMIDADE, COMPRESSAO, PROFUNDIDADEVINCO, FORCADEVINCO1, FORCADEVINCO2, FORCADEVINCO3, CHAPA,
            COMPOSICAO, FORMATOSIMPLEX, LARGURA, REFILOLARGURA, COMPRIMENTO, REFILOCOMPRIMENTO, MULTLARG,
            MULTCOMP, ARRANJO, REFUGOCLIENTE, PESOPECA, VINCOSLARGNORISCADOR, VINCOLARG1, VINCOLARG2,
            VINCOLARG3, VINCOLARG4, VINCOLARG5, VINCOLARG6, VINCOLARG7, VINCOLARG8, VINCOLARG9, VINCOLARG10,
            VINCOSCOMPNORISCADOR, VINCOCOMP1, VINCOCOMP2, VINCOCOMP3, VINCOCOMP4, VINCOCOMP5, VINCOCOMP6,
            VINCOCOMP7, VINCOCOMP8, VINCOCOMP9, VINCOCOMP10, TEARTAPE1, TEARTAPE2, TEARTAPE3, TEARTAPE4,
            LAP, PROLONGLAP, LAPNOCOMP, LAPINTERNO, LAPPRIMVINCO, REFILADO, REJEITO, REJEITOPECAS,
            RESINAINTERNA, RESINAINTERNASN, RESINAEXTERNA, RESINAEXTERNASN, ENDURECEDORMIOLO, ENDURECEDORMIOLOSN,
            FECHAMENTO, GRAMPOS, AMARRADO, FITILHOSLARGPACOTE, FITILHOSCOMPPACOTE, PALETIZADO, DESCRPALETIZADO,
            PACOTESLARGURA, PACOTESCOMPRIMENTO, PACOTESALTURA, PECASPORPACOTE, PECASPORPALETE, UNIDADESPORPALETE,
            PACOTESPORPALETE, FITASLARGPALETE, FITASCOMPPALETE, FACESOPPOSTAS, ESPELHO, CANTONEIRAS, FILME,
            ORELHASINVERTIDAS, FACA, CODFI, COR1, CONSUMOCOR1, VISCOSIDADECOR1, COR2, CONSUMOCOR2, VISCOSIDADECOR2,
            COR3, CONSUMOCOR3, VISCOSIDADECOR3, COR4, CONSUMOCOR4, VISCOSIDADECOR4, COR5, CONSUMOCOR5, VISCOSIDADECOR5,
            COR6, CONSUMOCOR6, VISCOSIDADECOR6, NRCORES, IMPCOMREGISTRO, DETALHECV, TOLMAIS, TOLMENOS, CONTRAONDA,
            TIPOOBS1, OBS1, TIPOOBS2, OBS2, TIPOOBS3, OBS3, TIPOOBS4, OBS4, TIPOOBS5, OBS5, TIPOOBS6, OBS6,
            TIPOOBS7, OBS7, TIPOOBS8, OBS8, TIPOOBS9, OBS9, DATAENTREGA1, DATAENTREGA2, QUANTIDADEPEDIDA,
            QUANTIDADEPEDIDAMIN, QUANTIDADEPEDIDAMAX, TIPOENTREGA, DESCTIPOENTREGA, LARGURAINTERNA, COMPRIMENTOINTERNO,
            ALTURAINTERNA, LARGPECA, COMPPECA, DIMADIC1, DIMADIC2, DIMADIC3, DIMADIC4, DIMADIC5, DIMADIC6, PRECOVENDA,
            CUSTOUNITTRANSP, CUSTOUNITVAR, CUSTOUNITFIXO, RESULTOPERACIONAL, MARGEMCONTRHORA, RECEITALIQUIDA,
            VENDALIQUIDA, MARGEMCONTR, PESOADIC, CUSTOUNITADIC, REGIAOORIGEM, DISTANCIA, FRETEINCLUSO,
            CONDICAODEPAGAMENTO, NRDECARROS, CUSTOEXTRAFRETE, PRECOFRETE, PRECOFERRAMENTAS, QUANTPREVISTA,
            DATACRIACAO, DATAENTREGAORIGINAL, NIVELURGENCIA, DATAULTIMAALTERACAOFT, FLAGESTOQUEOUTERCEIROS,
            DESCFLAGESTOQUEOUTERCEIROS, ADICIONAL1, POSSIVELDATAENTREGA, TIPODOPEDIDO, DESCRTIPODOPEDIDO,
            TEMPOEXPEDVIAGEM, IMPRIMELOGOTIPO, COMISSAODEVENDAS, VERSAODECUSTO, COMPPACOTE, LARGPACOTE,
            ALTURAPACOTE, COMPPALETEFECHADO, LARGPALETEFECHADO, ALTURAPALETEFECHADO, POROSIDADEMINIMO,
            PESOCAIXA, REFILOONDULADERA, TIPOCUSTOEXTRA, PEDCLIENTE, ITEMPEDCLIENTE, TIPOCAMINHAO, CONJUNTO,
            TRAVACOMPOSICAO, DESCRTRAVACOMPOSICAO, DATAPROMESSA, PRECORELACAO, PATHFIGURADOLASTRO,
            PATHFIGURADAFT, PRESSAODEARQUEAMENTO, EMPILHAMENTOMAXIMO, GRUPOPALETIZACAO, LIBERADOPROGEXPED,
            IDPALETE, REFERENCIAGRUPOPALETIZACAO, LOTEPILOTO, PEDIDO_ERP, ITEM_ERP, PRODUTO_ERP,
            DATACRIACAOREGISTRO, IDUNICOREGISTRO, OBSALTERACOES, IDUSUARIOULTMODIF, ULTMODIFICACAO,
            ORCAMENTO, ITEMORCAMENTO, CODREPRESENTANTE, CODSEGMENTO, AREAUTILCEDIDAFACA, AREABRUTAPECACOMREFILOS,
            AREABRUTAPECA, AREALIQUIDAPECA, AREABRUTACHAPA, AREALIQUIDACHAPA, VOLUMEPALETEFECHADOM3,
            VOLUMEPACOTEFECHADOM3, VOLUMEFECHADOPEDIDO, ORIGEMPEDIDO, DESCORIGEMPEDIDO, TIPOGERACAOPED,
            DESCTIPOGERACAOPED, IDFILIALEXPEDICAO, QTDIMPRESSOES, DATAHORAPRIMEIRAIMPRESSAO,
            IDUSUARIOPRIMEIRAIMPRESSAO, DATAHORAULTIMAIMPRESSAO, IDUSUARIOULTIMAIMPRESSAO, CHAVE_CHAPA
        ) VALUES (
            :IDPEDIDOS, :PEDIDO, :ITEM, :ITEMPEDIDO, :IDPEDVENDA, :IDITEMPEDVENDA, :STATUSPEDIDO,
            :DESCRSTATUSPEDIDO, :SUSPENSO, :SUSPOUCANCEL, :VERSAO, :IDCLIENTE, :IDLOJA, :IDLOCALENTREGA,
            :IDLOCALCOBRANCA, :REFERENCIA, :CODIGOREFERENCIA, :CODIGOEAN, :TIPOABNT, :IDTIPOFT, :IDTIPOFT2,
            :IDTIPOFT3, :IDTIPOFT4, :IDTIPOFT5, :PECASPORUNIDADE, :UNIDADESPORCONJUNTO, :PECASPORCONJUNTO,
            :EXIGELAUDO, :GRAMATURA, :MULLENMINIMO, :CRUSHMINIMO, :COLUNAMINIMO, :COBBINTMAXIMO, :COBBEXTMAXIMO,
            :COBBINT30MAXIMO, :COBBEXT30MAXIMO, :TESTEFISICOADICIONAL1, :PAT_INTERNO, :PAT_EXTERNO, :ESPESSURA,
            :UMIDADE, :COMPRESSAO, :PROFUNDIDADEVINCO, :FORCADEVINCO1, :FORCADEVINCO2, :FORCADEVINCO3, :CHAPA,
            :COMPOSICAO, :FORMATOSIMPLEX, :LARGURA, :REFILOLARGURA, :COMPRIMENTO, :REFILOCOMPRIMENTO, :MULTLARG,
            :MULTCOMP, :ARRANJO, :REFUGOCLIENTE, :PESOPECA, :VINCOSLARGNORISCADOR, :VINCOLARG1, :VINCOLARG2,
            :VINCOLARG3, :VINCOLARG4, :VINCOLARG5, :VINCOLARG6, :VINCOLARG7, :VINCOLARG8, :VINCOLARG9, :VINCOLARG10,
            :VINCOSCOMPNORISCADOR, :VINCOCOMP1, :VINCOCOMP2, :VINCOCOMP3, :VINCOCOMP4, :VINCOCOMP5, :VINCOCOMP6,
            :VINCOCOMP7, :VINCOCOMP8, :VINCOCOMP9, :VINCOCOMP10, :TEARTAPE1, :TEARTAPE2, :TEARTAPE3, :TEARTAPE4,
            :LAP, :PROLONGLAP, :LAPNOCOMP, :LAPINTERNO, :LAPPRIMVINCO, :REFILADO, :REJEITO, :REJEITOPECAS,
            :RESINAINTERNA, :RESINAINTERNASN, :RESINAEXTERNA, :RESINAEXTERNASN, :ENDURECEDORMIOLO, :ENDURECEDORMIOLOSN,
            :FECHAMENTO, :GRAMPOS, :AMARRADO, :FITILHOSLARGPACOTE, :FITILHOSCOMPPACOTE, :PALETIZADO, :DESCRPALETIZADO,
            :PACOTESLARGURA, :PACOTESCOMPRIMENTO, :PACOTESALTURA, :PECASPORPACOTE, :PECASPORPALETE, :UNIDADESPORPALETE,
            :PACOTESPORPALETE, :FITASLARGPALETE, :FITASCOMPPALETE, :FACESOPPOSTAS, :ESPELHO, :CANTONEIRAS, :FILME,
            :ORELHASINVERTIDAS, :FACA, :CODFI, :COR1, :CONSUMOCOR1, :VISCOSIDADECOR1, :COR2, :CONSUMOCOR2, :VISCOSIDADECOR2,
            :COR3, :CONSUMOCOR3, :VISCOSIDADECOR3, :COR4, :CONSUMOCOR4, :VISCOSIDADECOR4, :COR5, :CONSUMOCOR5, :VISCOSIDADECOR5,
            :COR6, :CONSUMOCOR6, :VISCOSIDADECOR6, :NRCORES, :IMPCOMREGISTRO, :DETALHECV, :TOLMAIS, :TOLMENOS, :CONTRAONDA,
            :TIPOOBS1, :OBS1, :TIPOOBS2, :OBS2, :TIPOOBS3, :OBS3, :TIPOOBS4, :OBS4, :TIPOOBS5, :OBS5, :TIPOOBS6, :OBS6,
            :TIPOOBS7, :OBS7, :TIPOOBS8, :OBS8, :TIPOOBS9, :OBS9, :DATAENTREGA1, :DATAENTREGA2, :QUANTIDADEPEDIDA,
            :QUANTIDADEPEDIDAMIN, :QUANTIDADEPEDIDAMAX, :TIPOENTREGA, :DESCTIPOENTREGA, :LARGURAINTERNA, :COMPRIMENTOINTERNO,
            :ALTURAINTERNA, :LARGPECA, :COMPPECA, :DIMADIC1, :DIMADIC2, :DIMADIC3, :DIMADIC4, :DIMADIC5, :DIMADIC6, :PRECOVENDA,
            :CUSTOUNITTRANSP, :CUSTOUNITVAR, :CUSTOUNITFIXO, :RESULTOPERACIONAL, :MARGEMCONTRHORA, :RECEITALIQUIDA,
            :VENDALIQUIDA, :MARGEMCONTR, :PESOADIC, :CUSTOUNITADIC, :REGIAOORIGEM, :DISTANCIA, :FRETEINCLUSO,
            :CONDICAODEPAGAMENTO, :NRDECARROS, :CUSTOEXTRAFRETE, :PRECOFRETE, :PRECOFERRAMENTAS, :QUANTPREVISTA,
            :DATACRIACAO, :DATAENTREGAORIGINAL, :NIVELURGENCIA, :DATAULTIMAALTERACAOFT, :FLAGESTOQUEOUTERCEIROS,
            :DESCFLAGESTOQUEOUTERCEIROS, :ADICIONAL1, :POSSIVELDATAENTREGA, :TIPODOPEDIDO, :DESCRTIPODOPEDIDO,
            :TEMPOEXPEDVIAGEM, :IMPRIMELOGOTIPO, :COMISSAODEVENDAS, :VERSAODECUSTO, :COMPPACOTE, :LARGPACOTE,
            :ALTURAPACOTE, :COMPPALETEFECHADO, :LARGPALETEFECHADO, :ALTURAPALETEFECHADO, :POROSIDADEMINIMO,
            :PESOCAIXA, :REFILOONDULADERA, :TIPOCUSTOEXTRA, :PEDCLIENTE, :ITEMPEDCLIENTE, :TIPOCAMINHAO, :CONJUNTO,
            :TRAVACOMPOSICAO, :DESCRTRAVACOMPOSICAO, :DATAPROMESSA, :PRECORELACAO, :PATHFIGURADOLASTRO,
            :PATHFIGURADAFT, :PRESSAODEARQUEAMENTO, :EMPILHAMENTOMAXIMO, :GRUPOPALETIZACAO, :LIBERADOPROGEXPED,
            :IDPALETE, :REFERENCIAGRUPOPALETIZACAO, :LOTEPILOTO, :PEDIDO_ERP, :ITEM_ERP, :PRODUTO_ERP,
            :DATACRIACAOREGISTRO, :IDUNICOREGISTRO, :OBSALTERACOES, :IDUSUARIOULTMODIF, :ULTMODIFICACAO,
            :ORCAMENTO, :ITEMORCAMENTO, :CODREPRESENTANTE, :CODSEGMENTO, :AREAUTILCEDIDAFACA, :AREABRUTAPECACOMREFILOS,
            :AREABRUTAPECA, :AREALIQUIDAPECA, :AREABRUTACHAPA, :AREALIQUIDACHAPA, :VOLUMEPALETEFECHADOM3,
            :VOLUMEPACOTEFECHADOM3, :VOLUMEFECHADOPEDIDO, :ORIGEMPEDIDO, :DESCORIGEMPEDIDO, :TIPOGERACAOPED,
            :DESCTIPOGERACAOPED, :IDFILIALEXPEDICAO, :QTDIMPRESSOES, :DATAHORAPRIMEIRAIMPRESSAO,
            :IDUSUARIOPRIMEIRAIMPRESSAO, :DATAHORAULTIMAIMPRESSAO, :IDUSUARIOULTIMAIMPRESSAO, :CHAVE_CHAPA
        )
    """

    dst = _make_oracle_conn()
    try:
        cur = dst.cursor()
        
        # Configurar inputs específicos para TIMESTAMP
        for param in payload:
            for date_field in ['DATAENTREGA1', 'DATAENTREGA2', 'DATACRIACAO', 'DATAENTREGAORIGINAL', 'DATAULTIMAALTERACAOFT', 'DATAPROMESSA', 'DATACRIACAOREGISTRO', 'ULTMODIFICACAO', 'DATAHORAPRIMEIRAIMPRESSAO', 'DATAHORAULTIMAIMPRESSAO']:
                if date_field in param and isinstance(param[date_field], datetime):
                    if param[date_field].microsecond == 0:
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
# DAG para PEDIDOS
# -----------------
with DAG(
    dag_id="etl_pedidos",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "sqlserver", "oracle", "pedidos"],
):
    merge_upsert = PythonOperator(
        task_id="merge_upsert_pedidos",
        python_callable=etl_pedidos,
    )