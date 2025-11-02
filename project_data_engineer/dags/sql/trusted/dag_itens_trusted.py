from __future__ import annotations
from datetime import datetime, date
from typing import Any, Dict, List

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import oracledb
import uuid
import re

MSSQL_CONN_ID = "mssql_src"
ORACLE_CONN_ID = "oracle_trusted"  # destino TRS

def _make_mssql_engine():
    c = BaseHook.get_connection(MSSQL_CONN_ID)
    extra = c.extra_dejson or {}
    driver = extra.get("driver", "ODBC Driver 17 for SQL Server")
    trust = extra.get("TrustServerCertificate", "yes")
    odbc_connect = (
        f"DRIVER={{{driver}}};"
        f"SERVER={c.host},{c.port or 1433};"
        f"DATABASE={c.schema};"
        f"UID={c.login};PWD={c.password};"
        f"TrustServerCertificate={trust};"
    )
    url = URL.create("mssql+pyodbc", query={"odbc_connect": odbc_connect})
    return create_engine(url, fast_executemany=True)

def _make_oracle_conn():
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

ORACLE_COLS = [
    "ITEM","CONJUNTO","IDTIPOFT2","IDTIPOIPI","IDCLASSFISCAL","IDFAMILIA",
    "ESTADOFT_DETEC","TEXTOESTADOFT_DETEC","RAZAOESTADOFT","STATUSFT","TEXTOSTATUSFT",
    "VERSAO","OBSVERSAO","IDCLIENTE","REFERENCIA","CODIGOREFERENCIA","TIPOABNT",
    "PECASPORUNIDADE","UNIDADESPORCONJUNTO","PECASPORCONJUNTO","EXIGELAUDO","GRAMATURA",
    "MULLENMINIMO","COLUNAMINIMO","COBBINTMAXIMO","COBBEXTMAXIMO","ESPESSURA","COMPRESSAO",
    "COMPOSICAO","LARGURA","REFILOLARGURA","COMPRIMENTO","REFILOCOMPRIMENTO","MULTLARG",
    "MULTCOMP","ARRANJO","REFUGOCLIENTE","VINCOLARG1","VINCOLARG2","VINCOLARG3",
    "VINCOCOMP1","VINCOCOMP2","VINCOCOMP3","VINCOCOMP4","VINCOCOMP5","LAP","PROLONGLAP",
    "LAPNOCOMP","TEXTO_LAPNOCOMP","LAPINTERNO","TEXTO_LAPINTERNO","LAPPRIMVINCO","REFILADO",
    "RESINAINTERNA","FECHAMENTO","AMARRADO","FITILHOSLARGPACOTE","PALETIZADO",
    "PACOTESLARGURA","PACOTESCOMPRIMENTO","PACOTESALTURA","PECASPORPACOTE","PECASPORPALETE",
    "PACOTESPORPALETE","UNIDADESPORPALETE","FITASLARGPALETE","FITASCOMPPALETE","ESPELHO","FILME",
    "FACA","CODFI","COR1","CONSUMOCOR1","COR2","CONSUMOCOR2","COR3","CONSUMOCOR3","COR4","CONSUMOCOR4",
    "NRCORES","TOLMAIS","TOLMENOS","TIPOOBS1","OBS1","TIPOOBS2","OBS2","TIPOOBS3","OBS3","TIPOOBS4",
    "OBS4","TIPOOBS5","LARGURAINTERNA","COMPRIMENTOINTERNO","ALTURAINTERNA","LARGPECA","COMPPECA",
    "DIMADIC1","DIMADIC2","IMPRIMELOGOTIPO","USUARIOCRIACAO","USUARIO","DATAMODIF","DATACRIACAO",
    "COMPPACOTE","LARGPACOTE","ALTURAPACOTE","COMMPALETEFECHADO","LARGPALETEFECHADO",
    "ALTURAPALETEFECHADO","PESOCAIXA","PROJETO","DESCRTRAVACOMPOSICAO","PATHFIGURADOLASTRO",
    "EMPILHAMENTOMAXIMO","IDPALETE","IDUNICOREGISTRO","NRPEDSPILOTO","AREABRUTAPECACOMREFILOS",
    "AREABRUTAPECA","AREALIQUIDAPECA","AREABRUTACHAPA","AREALIQUIDACHAPA",
    "VOLUMEPALETEFECHADOM3","VOLUMEPACOTEFECHADOM3","RESUMOCHAPA","COMPLEMENTOCHAPA"
]

REQUIRED_NOT_NULL = {
    "ITEM","CONJUNTO","ESTADOFT_DETEC","RAZAOESTADOFT","VERSAO",
    "IDCLIENTE","REFERENCIA","EXIGELAUDO","REFILOLARGURA","REFILOCOMPRIMENTO",
    "MULTLARG","MULTCOMP","REFUGOCLIENTE","LAP","LAPNOCOMP","LAPINTERNO",
    "LAPPRIMVINCO","REFILADO","AMARRADO","PALETIZADO","ESPELHO","FILME",
    "IMPRIMELOGOTIPO","IDUNICOREGISTRO"
}

TIMESTAMP_COLS = {"DATAMODIF","DATACRIACAO"}
BINARY_DOUBLE_COLS = {
    "PECASPORUNIDADE","UNIDADESPORCONJUNTO","PECASPORCONJUNTO",
    "MULLENMINIMO","COLUNAMINIMO","COBBINTMAXIMO","COBBEXTMAXIMO",
    "ESPESSURA","COMPRESSAO","REFUGOCLIENTE","UNIDADESPORPALETE","PESOCAIXA",
    "AREABRUTAPECACOMREFILOS","AREABRUTAPECA","AREALIQUIDAPECA",
    "AREABRUTACHAPA","AREALIQUIDACHAPA","VOLUMEPALETEFECHADOM3","VOLUMEPACOTEFECHADOM3",
}
RAW16_COLS = {"IDUNICOREGISTRO"}

RENAME_MAP = {
    "Item":"ITEM","Conjunto":"CONJUNTO","idTipoFT2":"IDTIPOFT2",
    "IDTipoIPI":"IDTIPOIPI","IDClassFiscal":"IDCLASSFISCAL","IDFamilia":"IDFAMILIA",
    "EstadoFT_Detec":"ESTADOFT_DETEC","TextoEstadoFT_Detec":"TEXTOESTADOFT_DETEC",
    "RazaoEstadoFT":"RAZAOESTADOFT","StatusFT":"STATUSFT","TextoStatusFT":"TEXTOSTATUSFT",
    "Versao":"VERSAO","ObsVersao":"OBSVERSAO","IDCliente":"IDCLIENTE","Referencia":"REFERENCIA",
    "CodigoReferencia":"CODIGOREFERENCIA","TipoABNT":"TIPOABNT",
    "PecasPorUnidade":"PECASPORUNIDADE","UnidadesPorConjunto":"UNIDADESPORCONJUNTO",
    "PecasPorConjunto":"PECASPORCONJUNTO","ExigeLaudo":"EXIGELAUDO","Gramatura":"GRAMATURA",
    "MullenMinimo":"MULLENMINIMO","ColunaMinimo":"COLUNAMINIMO",
    "CobbIntMaximo":"COBBINTMAXIMO","CobbExtMaximo":"COBBEXTMAXIMO",
    "Espessura":"ESPESSURA","Compressao":"COMPRESSAO","Composicao":"COMPOSICAO",
    "Largura":"LARGURA","RefiloLargura":"REFILOLARGURA","Comprimento":"COMPRIMENTO",
    "RefiloComprimento":"REFILOCOMPRIMENTO","MultLarg":"MULTLARG","MultComp":"MULTCOMP",
    "Arranjo":"ARRANJO","RefugoCliente":"REFUGOCLIENTE","VincoLarg1":"VINCOLARG1",
    "VincoLarg2":"VINCOLARG2","VincoLarg3":"VINCOLARG3","VincoComp1":"VINCOCOMP1",
    "VincoComp2":"VINCOCOMP2","VincoComp3":"VINCOCOMP3","VincoComp4":"VINCOCOMP4",
    "VincoComp5":"VINCOCOMP5","Lap":"LAP","ProlongLap":"PROLONGLAP","LapNoComp":"LAPNOCOMP",
    "TextoLapNoComp":"TEXTO_LAPNOCOMP","LapInterno":"LAPINTERNO","TextoLapInterno":"TEXTO_LAPINTERNO",
    "LapPrimVinco":"LAPPRIMVINCO","Refilado":"REFILADO","ResinaInterna":"RESINAINTERNA",
    "Fechamento":"FECHAMENTO","Amarrado":"AMARRADO","FitilhosLargPacote":"FITILHOSLARGPACOTE",
    "Paletizado":"PALETIZADO","PacotesLargura":"PACOTESLARGURA",
    "PacotesComprimento":"PACOTESCOMPRIMENTO","PacotesAltura":"PACOTESALTURA",
    "PecasPorPacote":"PECASPORPACOTE","PecasPorPalete":"PECASPORPALETE",
    "PacotesPorPalete":"PACOTESPORPALETE","UnidadesPorPalete":"UNIDADESPORPALETE",
    "FitasLargPalete":"FITASLARGPALETE","FitasCompPalete":"FITASCOMPPALETE",
    "Espelho":"ESPELHO","Filme":"FILME","Faca":"FACA","CodFI":"CODFI",
    "Cor1":"COR1","ConsumoCor1":"CONSUMOCOR1","Cor2":"COR2","ConsumoCor2":"CONSUMOCOR2",
    "Cor3":"COR3","ConsumoCor3":"CONSUMOCOR3","Cor4":"COR4","ConsumoCor4":"CONSUMOCOR4",
    "NrCores":"NRCORES","TolMais":"TOLMAIS","TolMenos":"TOLMENOS","TipoObs1":"TIPOOBS1",
    "Obs1":"OBS1","TipoObs2":"TIPOOBS2","Obs2":"OBS2","TipoObs3":"TIPOOBS3","Obs3":"OBS3",
    "TipoObs4":"TIPOOBS4","Obs4":"OBS4","TipoObs5":"TIPOOBS5",
    "LarguraInterna":"LARGURAINTERNA","ComprimentoInterno":"COMPRIMENTOINTERNO",
    "AlturaInterna":"ALTURAINTERNA","LargPeca":"LARGPECA","CompPeca":"COMPPECA",
    "DimAdic1":"DIMADIC1","DimAdic2":"DIMADIC2",
    "ImprimeLogotipo":"IMPRIMELOGOTIPO","UsuarioCriacao":"USUARIOCRIACAO","Usuario":"USUARIO",
    "DataModif":"DATAMODIF","DataCriacao":"DATACRIACAO","CompPacote":"COMPPACOTE",
    "LargPacote":"LARGPACOTE","AlturaPacote":"ALTURAPACOTE",
    "CompPaleteFechado":"COMMPALETEFECHADO","LargPaleteFechado":"LARGPALETEFECHADO",
    "AlturaPaleteFechado":"ALTURAPALETEFECHADO","PesoCaixa":"PESOCAIXA","Projeto":"PROJETO",
    "DescrTravaComposicao":"DESCRTRAVACOMPOSICAO","PathFiguraDoLastro":"PATHFIGURADOLASTRO",
    "EmpilhamentoMaximo":"EMPILHAMENTOMAXIMO","IDPalete":"IDPALETE",
    "IDUnicoRegistro":"IDUNICOREGISTRO","NrPedsLotePiloto":"NRPEDSPILOTO",
    "AreaBrutaPecaComRefilos":"AREABRUTAPECACOMREFILOS","AreaBrutaPeca":"AREABRUTAPECA",
    "AreaLiquidaPeca":"AREALIQUIDAPECA","AreaBrutaChapa":"AREABRUTACHAPA",
    "AreaLiquidaChapa":"AREALIQUIDACHAPA","VolumePaleteFechadoM3":"VOLUMEPALETEFECHADOM3",
    "VolumePacoteFechadoM3":"VOLUMEPACOTEFECHADOM3","ResumoChapa":"RESUMOCHAPA",
    "ComplementoChapa":"COMPLEMENTOCHAPA",
}

SQL_SELECT = text("""
SELECT
    Item, Conjunto, idTipoFT2, IDTipoIPI, IDClassFiscal, IDFamilia,
    EstadoFT_Detec, TextoEstadoFT_Detec, RazaoEstadoFT, StatusFT, TextoStatusFT,
    Versao, ObsVersao, IDCliente, Referencia, CodigoReferencia, TipoABNT,
    PecasPorUnidade, UnidadesPorConjunto, PecasPorConjunto, ExigeLaudo, Gramatura,
    MullenMinimo, ColunaMinimo, CobbIntMaximo, CobbExtMaximo, Espessura, Compressao,
    Composicao, Largura, RefiloLargura, Comprimento, RefiloComprimento, MultLarg, MultComp,
    Arranjo, RefugoCliente, VincoLarg1, VincoLarg2, VincoLarg3, VincoComp1, VincoComp2,
    VincoComp3, VincoComp4, VincoComp5, Lap, ProlongLap, LapNoComp, TextoLapNoComp,
    LapInterno, TextoLapInterno, LapPrimVinco, Refilado, ResinaInterna, Fechamento,
    Amarrado, FitilhosLargPacote, Paletizado, PacotesLargura, PacotesComprimento,
    PacotesAltura, PecasPorPacote, PecasPorPalete, PacotesPorPalete, UnidadesPorPalete,
    FitasLargPalete, FitasCompPalete, Espelho, Filme, Faca, CodFI,
    Cor1, ConsumoCor1, Cor2, ConsumoCor2, Cor3, ConsumoCor3, Cor4, ConsumoCor4,
    NrCores, TolMais, TolMenos, TipoObs1, Obs1, TipoObs2, Obs2, TipoObs3, Obs3, TipoObs4, Obs4,
    TipoObs5, LarguraInterna, ComprimentoInterno, AlturaInterna, LargPeca, CompPeca,
    DimAdic1, DimAdic2, ImprimeLogotipo, UsuarioCriacao, Usuario, DataModif, DataCriacao,
    CompPacote, LargPacote, AlturaPacote, CompPaleteFechado, LargPaleteFechado, AlturaPaleteFechado,
    PesoCaixa, Projeto, DescrTravaComposicao, PathFiguraDoLastro, EmpilhamentoMaximo, IDPalete,
    IDUnicoRegistro, NrPedsLotePiloto, AreaBrutaPecaComRefilos, AreaBrutaPeca, AreaLiquidaPeca,
    AreaBrutaChapa, AreaLiquidaChapa, VolumePaleteFechadoM3, VolumePacoteFechadoM3,
    ResumoChapa, ComplementoChapa
FROM ITENS
""")

def _to_date_like(v: Any) -> Any:
    if v is None or isinstance(v, (datetime, date)):
        return v
    try:
        return datetime.fromisoformat(str(v))
    except Exception:
        return v

_guid_cleaner = re.compile(r"[{}-]", re.IGNORECASE)
def _to_raw16_uuid(val: Any) -> bytes | None:
    if val is None:
        return None
    if isinstance(val, (bytes, bytearray)):
        b = bytes(val)
        return b if len(b) == 16 else None
    s = str(val).strip()
    if not s:
        return None
    try:
        return uuid.UUID(s).bytes
    except Exception:
        pass
    s2 = _guid_cleaner.sub("", s)
    if len(s2) == 32:
        try:
            return uuid.UUID(s2).bytes
        except Exception:
            return None
    return None

def _row_to_payload(row: Dict[str, Any]) -> Dict[str, Any] | None:
    out: Dict[str, Any] = {}

    for src_key, val in row.items():
        tgt = RENAME_MAP.get(src_key, src_key.upper())

        if tgt in TIMESTAMP_COLS:
            dt_val = _to_date_like(val)
            if dt_val is not None and isinstance(dt_val, datetime):
                out[tgt] = dt_val.strftime('%Y/%m/%d %H:%M:%S.000')
            else:
                out[tgt] = dt_val
            continue

        if tgt in RAW16_COLS:
            raw = _to_raw16_uuid(val)
            if raw is None:
                return None
            out[tgt] = raw
            continue

        if tgt in BINARY_DOUBLE_COLS and val is not None:
            try:
                out[tgt] = float(val)
            except Exception:
                out[tgt] = None
            continue

        out[tgt] = (None if val is None else str(val))

    # garante chaves ausentes
    for col in ORACLE_COLS:
        out.setdefault(col, None)

    # >>> ponto crítico: Oracle trata "" como NULL; use valor não-vazio
    if out.get("RAZAOESTADOFT") is None or str(out["RAZAOESTADOFT"]).strip() == "":
        out["RAZAOESTADOFT"] = "N/A"

    # valida obrigatórios (tratando "" como vazio também)
    for k in REQUIRED_NOT_NULL:
        v = out.get(k)
        if v is None:
            return None
        if isinstance(v, str) and v.strip() == "":
            return None

    return out

def etl_itens_trusted(**context):
    mssql = _make_mssql_engine()
    with mssql.connect() as conn:
        rows = [dict(r) for r in conn.execute(SQL_SELECT).mappings().all()]
    if not rows:
        return

    payload_all: List[Dict[str, Any] | None] = [_row_to_payload(r) for r in rows]
    payload = [p for p in payload_all if p is not None]

    skipped = len(payload_all) - len(payload)
    if skipped:
        print(f"[ITENS] Registros descartados por validação (NOT NULL/RAW16/strings vazias): {skipped}")

    if not payload:
        print("[ITENS] Nenhum registro válido após validação.")
        return

    pk = "ITEM"
    non_pk_cols = [c for c in ORACLE_COLS if c != pk]

    select_dual = ", ".join([
        f"TO_TIMESTAMP(:{c}, 'YYYY/MM/DD HH24:MI:SS.FF3') AS {c}" if c in TIMESTAMP_COLS else f":{c} {c}" 
        for c in ORACLE_COLS
    ])
    update_set  = ", ".join([f"d.{c} = s.{c}" for c in non_pk_cols])
    insert_cols = ", ".join(ORACLE_COLS)
    insert_vals = ", ".join([f"s.{c}" for c in ORACLE_COLS])

    merge_sql = f"MERGE INTO ITENS d USING (SELECT {select_dual} FROM dual) s ON (d.{pk} = s.{pk}) WHEN MATCHED THEN UPDATE SET {update_set} WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})"

    conn = _make_oracle_conn()
    try:
        cur = conn.cursor()
        cur.executemany(merge_sql, payload)
        conn.commit()
    finally:
        conn.close()

with DAG(
    dag_id="etl_itens_trusted",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl","sqlserver","oracle","itens","trusted"],
):
    PythonOperator(
        task_id="merge_upsert_itens",
        python_callable=etl_itens_trusted,
    )