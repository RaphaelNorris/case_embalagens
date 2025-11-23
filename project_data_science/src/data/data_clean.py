"""
DataFrame cleaning utilities for Oracle ETL.

This module collects a set of helper functions and per‑table cleaning
functions used to transform DataFrames extracted from the “trusted”
layer of an Oracle data warehouse into a canonical “refined” layout.

Each function mirrors the logic found in the Airflow DAGs for the
corresponding table.  Missing values, empty strings and numeric NaNs
are normalised according to the prefix of each column name:

* ``TX_`` columns never return ``None``; nulls become a space (``" "``).
* ``FL_`` columns are single character flags; they return ``"0"`` or ``"1"``
  depending on whether the input can be interpreted as False/True.
* ``VL_`` and ``QT_`` numeric columns return 0 when the source is empty.
* ``ID_`` and ``CD_`` key columns return ``"-1"`` when missing.
* ``ST_`` status columns return a single space when missing.
* ``DT_`` date/time columns are converted to Python ``datetime`` objects
  and use a sentinel date (``2999-01-01``) when the input is invalid or null.

These helpers can be combined to build custom cleaning functions for
other tables following the same conventions.  See the individual
``clean_*`` functions for examples of how to apply them.

Note: The functions below do not perform any database I/O.  They assume
that DataFrames have already been populated via ``pandas.read_sql`` or
equivalent.  Connection details and SQL queries should be handled
externally.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import numpy as np
import pandas as pd

###############################################################################
# Generic helper functions
###############################################################################


def handle_nan(value: Any, nan_value: Any) -> Any:
    """
    Replace missing or empty values with a default.

    Parameters
    ----------
    value : Any
        The value to examine.  Missing values (None/NaN) or empty strings are
        considered invalid.
    nan_value : Any
        The replacement to return when ``value`` is considered missing.

    Returns
    -------
    Any
        ``value`` unchanged if present and not empty, otherwise ``nan_value``.
    """
    if pd.isna(value):
        return nan_value
    if isinstance(value, str) and value.strip() == "":
        return nan_value
    if isinstance(value, (int, float)) and (value == 0 or value == -1):
        return value
    try:
        if isinstance(value, float) and np.isnan(value):
            return nan_value
    except Exception:
        pass
    return value


def convert_to_varchar(
    value: Any, nan_value: str, field_name: Optional[str] = None
) -> str:
    """
    Convert a value into a string suitable for an Oracle VARCHAR column.

    Parameters
    ----------
    value : Any
        The original value.
    nan_value : str
        The fallback string when ``value`` is considered missing.
    field_name : str, optional
        The name of the column being converted.  When starting with ``FL_``
        the function interprets truthiness.  When starting with ``TX_``
        it guarantees a non-null result.

    Returns
    -------
    str
        A normalised string representation of the input.
    """
    # Normalise floats that represent integers.  Codes and identifiers are
    # sometimes read as floats (e.g. 1.0) from SQL but should not carry a
    # decimal point.  By converting them here, all calls to this helper will
    # produce clean integer strings for whole numbers.
    if isinstance(value, float) and not np.isnan(value) and float(value).is_integer():
        value = int(value)

    # Flags: return "0" or "1"
    if field_name and field_name.startswith("FL_"):
        if pd.isna(value):
            return "0"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (int, float)):
            # Already normalised floats above; treat numerics directly
            if isinstance(value, float) and np.isnan(value):
                return "0"
            return "1" if value != 0 else "0"
        if isinstance(value, str):
            v = value.strip().upper()
            if v in ("1", "Y", "S", "TRUE", "T", "SIM"):
                return "1"
            if v in ("0", "N", "FALSE", "F", "NAO", "NÃO"):
                return "0"
            try:
                num = int(value)
                return "1" if num != 0 else "0"
            except Exception:
                return "1" if v else "0"
        if isinstance(value, bytes):
            return "0" if value in (b"\x00", b"") else "1"
        return "1" if bool(value) else "0"

    # Text columns: never return None
    if field_name and field_name.startswith("TX_"):
        if pd.isna(value):
            return " "
        if isinstance(value, str):
            return value.strip() or ""
        try:
            s = str(value)
            return s.strip() or ""
        except Exception:
            return ""

    # Generic string conversion
    if pd.isna(value):
        return nan_value
    if isinstance(value, str):
        return value.strip() or nan_value
    try:
        s = str(value)
        return s.strip() or nan_value
    except Exception:
        return nan_value


def convert_to_number(value: Any, nan_value: float | int) -> float | int:
    if pd.isna(value):
        return nan_value
    if isinstance(value, (int, float)):
        if isinstance(value, float) and np.isnan(value):
            return nan_value
        return value
    try:
        s = str(value).strip()
        if s == "":
            return nan_value
        return float(s) if "." in s else int(s)
    except Exception:
        return nan_value


def convert_to_timestamp(
    value: Any, nan_date: Optional[str] = None
) -> datetime | pd.NaT:
    if pd.isna(value):
        if nan_date:
            return datetime.strptime(nan_date, "%Y-%m-%d")
        return pd.NaT
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in (
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%y %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        try:
            parsed = pd.to_datetime(value, errors="coerce")
            if pd.isna(parsed):
                raise ValueError
            return parsed.to_pydatetime()
        except Exception:
            pass
    try:
        return datetime.combine(value, datetime.min.time())  # type: ignore[arg-type]
    except Exception:
        pass
    if nan_date:
        return datetime.strptime(nan_date, "%Y-%m-%d")
    return pd.NaT


###############################################################################
# Per‑table cleaning functions
###############################################################################


def clean_tarefcon(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e padroniza os dados da tabela TAREFCON (ordens de produção).
    Aplica prefixos, converte tipos e trata nulos.
    """
    df = df.copy()
    df.columns = [c.upper() for c in df.columns]
    data: dict[str, pd.Series] = {}

    def varchar(src: str, default: str, name: str) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_varchar(v, default, name))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    def number(src: str, default: float) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_number(v, default))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    def flag(src: str, name: str) -> pd.Series:
        if src not in df.columns:
            return pd.Series(["0"] * len(df))
        return df[src].apply(lambda v: convert_to_varchar(handle_nan(v, 0), "0", name))

    def ts(src: str) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_timestamp(v, "2999-12-31"))
            if src in df.columns
            else pd.Series([datetime.strptime("2999-12-31", "%Y-%m-%d")] * len(df))
        )

    # Campos categóricos / chaves
    data["CD_MAQUINA"] = varchar("MAQUINA", "-1", "CD_MAQUINA")
    data["CD_PARADAOUCONV"] = varchar("CODIGOPARADAOUCONV", "-1", "CD_PARADAOUCONV")
    data["CD_TURMA"] = varchar("TURMA", "-1", "CD_TURMA")
    data["CD_OP"] = varchar("OP", "-1", "CD_OP")
    data["CD_PEDIDO"] = varchar("PEDIDO", "-1", "CD_PEDIDO")
    data["CD_ITEM"] = varchar("ITEM", "-1", "CD_ITEM")
    data["CD_USUARIO"] = varchar("USUARIO", "-1", "CD_USUARIO")
    data["CD_ORIGEM_REGISTRO"] = varchar("ORIGEMREGISTRO", "-1", "CD_ORIGEM_REGISTRO")
    data["CD_FACA"] = varchar("FACA", "-1", "CD_FACA")

    # Flags
    data["FL_PARADA"] = flag("FLAGPARADA", "FL_PARADA")
    data["FL_REPROGRAMACAO"] = flag("REPROGRAMACAO", "FL_REPROGRAMACAO")
    data["FL_SKIPFEED"] = flag("SKIPFEED", "FL_SKIPFEED")

    # Númericos
    data["QT_ARRANJO"] = number("ARRANJO", 0)
    data["VL_GRAMATURA"] = number("GRAMATURA", 0)
    data["QT_PROGRAMADA"] = number("QUANTIDADEPROGRAMADA", 0)
    data["QT_CHAPASALIMENTADAS"] = number("CHAPASALIMENTADAS", 0)
    data["QT_PRODUZIDA"] = number("QUANTIDADEPRODUZIDA", 0)
    data["QT_AJUSTE"] = number("QUANTIDADEAJUSTE", 0)
    data["VL_DURACAO_PREVISTA"] = number("DURACAOPREVISTA", 0)
    data["VL_DURACAO"] = number("DURACAO", 0)

    # Datas e horários
    data["DT_INICIO"] = ts("INICIO")
    data["DT_FIM"] = ts("FIM")
    data["DT_TURMA"] = ts("DIADATURMA")

    # Textos descritivos
    data["TX_DESC_ORIGEM_REGISTRO"] = varchar(
        "DESCORIGEMREGISTRO", "", "TX_DESC_ORIGEM_REGISTRO"
    )
    data["TX_OPONDULADA"] = varchar("OPONDULADA", "", "TX_OPONDULADA")
    data["ID_CLIENTE"] = varchar("IDCLIENTE", "-1", "ID_CLIENTE")

    refined = pd.DataFrame(data)
    # Tipagem final
    str_cols = [
        c for c in refined.columns if c.startswith(("CD_", "ID_", "TX_", "FL_"))
    ]
    refined[str_cols] = refined[str_cols].astype("string[pyarrow]")
    num_cols = [c for c in refined.columns if c.startswith(("VL_", "QT_"))]
    refined[num_cols] = refined[num_cols].astype(float)
    return refined


def clean_pedidos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e padroniza os dados da tabela PEDIDOS.
    """
    df = df.copy()
    df.columns = [c.upper() for c in df.columns]
    data: dict[str, pd.Series] = {}

    def varchar(src: str, default: str, name: str) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_varchar(v, default, name))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    def number(src: str, default: float) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_number(v, default))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    def ts(src: str) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_timestamp(v, "2999-12-31"))
            if src in df.columns
            else pd.Series([datetime.strptime("2999-12-31", "%Y-%m-%d")] * len(df))
        )

    # Identificadores
    data["CD_PEDIDO"] = varchar("PEDIDO", "-1", "CD_PEDIDO")

    data["CD_ITEM"] = varchar("ITEM", "-1", "CD_ITEM")
    data["ID_CLIENTE"] = varchar("IDCLIENTE", "-1", "ID_CLIENTE")
    data["CD_PALETE"] = varchar("IDPALETE", "-1", "CD_PALETE")
    data["CD_TIPOFT2"] = varchar("IDTIPOFT2", "-1", "CD_TIPOFT2")
    data["CD_REFERENCIA"] = varchar("CODIGOREFERENCIA", "-1", "CD_REFERENCIA")

    # Datas
    data["DT_ENTREGA2"] = ts("DATAENTREGA2")
    data["DT_ENTREGAORIGINAL"] = ts("DATAENTREGAORIGINAL")

    # Flags
    data["FL_AMARRADO"] = (
        df["AMARRADO"].apply(
            lambda v: convert_to_varchar(handle_nan(v, 0), "0", "FL_AMARRADO")
        )
        if "AMARRADO" in df.columns
        else pd.Series(["0"] * len(df))
    )
    data["FL_CHAPA"] = (
        df["CHAPA"].apply(
            lambda v: convert_to_varchar(handle_nan(v, 0), "0", "FL_CHAPA")
        )
        if "CHAPA" in df.columns
        else pd.Series(["0"] * len(df))
    )
    data["FL_EXIGELAUDO"] = (
        df["EXIGELAUDO"].apply(
            lambda v: convert_to_varchar(handle_nan(v, 0), "0", "FL_EXIGELAUDO")
        )
        if "EXIGELAUDO" in df.columns
        else pd.Series(["0"] * len(df))
    )
    data["FL_PALETIZADO"] = (
        df["PALETIZADO"].apply(
            lambda v: convert_to_varchar(handle_nan(v, 0), "0", "FL_PALETIZADO")
        )
        if "PALETIZADO" in df.columns
        else pd.Series(["0"] * len(df))
    )
    data["FL_REFILADO"] = (
        df["REFILADO"].apply(
            lambda v: convert_to_varchar(handle_nan(v, 0), "0", "FL_REFILADO")
        )
        if "REFILADO" in df.columns
        else pd.Series(["0"] * len(df))
    )
    data["FL_RESINAINTERNA"] = (
        df["RESINAINTERNA"].apply(
            lambda v: convert_to_varchar(handle_nan(v, 0), "0", "FL_RESINAINTERNA")
        )
        if "RESINAINTERNA" in df.columns
        else pd.Series(["0"] * len(df))
    )
    data["FL_SUSPENSO"] = (
        df["SUSPENSO"].apply(
            lambda v: convert_to_varchar(handle_nan(v, 0), "0", "FL_SUSPENSO")
        )
        if "SUSPENSO" in df.columns
        else pd.Series(["0"] * len(df))
    )
    data["FL_TIPOENTREGA"] = (
        df["TIPOENTREGA"].apply(
            lambda v: convert_to_varchar(handle_nan(v, 0), "0", "FL_TIPOENTREGA")
        )
        if "TIPOENTREGA" in df.columns
        else pd.Series(["0"] * len(df))
    )

    # SUSPOUCANCEL → transformar em flag 0/1 (Sim → 1, Não → 0)
    if "SUSPOUCANCEL" in df.columns:
        data["FL_SUSPOUCANCEL"] = df["SUSPOUCANCEL"].apply(
            lambda v: 1 if str(v).strip().lower() in ("sim", "1", "s", "true") else 0
        )
    else:
        data["FL_SUSPOUCANCEL"] = pd.Series([0] * len(df))

    # Textos e descrições
    data["ST_PEDIDO"] = varchar("STATUSPEDIDO", " ", "ST_PEDIDO")
    data["TX_DESCRSTATUSPEDIDO"] = varchar(
        "DESCRSTATUSPEDIDO", "", "TX_DESCRSTATUSPEDIDO"
    )
    data["TX_DESCRTIPODOPEDIDO"] = varchar(
        "DESCRTIPODOPEDIDO", "", "TX_DESCRTIPODOPEDIDO"
    )
    data["TX_DESCTIPOENTREGA"] = varchar("DESCTIPOENTREGA", "", "TX_DESCTIPOENTREGA")
    data["TX_TIPOABNT"] = varchar("TIPOABNT", "", "TX_TIPOABNT")
    data["TX_COMPOSICAO"] = varchar("COMPOSICAO", "", "TX_COMPOSICAO")

    # Códigos e referências de materiais
    data["CD_ESPELHO"] = varchar("ESPELHO", "-1", "CD_ESPELHO")
    data["CD_FILME"] = varchar("FILME", "-1", "CD_FILME")
    data["CD_FACA"] = varchar("FACA", "-1", "CD_FACA")

    # Números e medidas
    num_cols = {
        "QT_ARRANJO": "ARRANJO",
        "QT_COBBINTMAXIMO": "COBBINTMAXIMO",
        "QT_NRCORES": "NRCORES",
        "QT_PEDIDA": "QUANTIDADEPEDIDA",
        "QT_PEDIDAMAX": "QUANTIDADEPEDIDAMAX",
        "QT_PEDIDAMIN": "QUANTIDADEPEDIDAMIN",
        "QT_PROLONGLAP": "PROLONGLAP",
        "QT_PECASPORPACOTE": "PECASPORPACOTE",
        "QT_PECASPORPALETE": "PECASPORPALETE",
        "QT_UNIDADESPORPALETE": "UNIDADESPORPALETE",
        "QT_PACOTESPORPALETE": "PACOTESPORPALETE",
        "VL_LAPINTERNO": "LAPINTERNO",
        "VL_LAPNOCOMP": "LAPNOCOMP",
        "VL_GRAMATURA": "GRAMATURA",
        "VL_COMPRIMENTO": "COMPRIMENTO",
        "VL_LARGURA": "LARGURA",
        "VL_ALTURAINTERNA": "ALTURAINTERNA",
        "VL_REFUGOCLIENTE": "REFUGOCLIENTE",
        "VL_PESOPECA": "PESOPECA",
        "VL_PESOCAIXA": "PESOCAIXA",
        "VL_AREABRUTAPECA": "AREABRUTAPECA",
        "VL_AREALIQUIDAPECA": "AREALIQUIDAPECA",
        "VL_AREABRUTACHAPA": "AREABRUTACHAPA",
        "VL_AREALIQUIDACHAPA": "AREALIQUIDACHAPA",
        "VL_VOLUMEFECHADOPEDIDO": "VOLUMEFECHADOPEDIDO",
        "VL_VOLUMEPACOTEFECHADOM3": "VOLUMEPACOTEFECHADOM3",
        "VL_VOLUMEPALETEFECHADOM3": "VOLUMEPALETEFECHADOM3",
        # novos, com base no schema:
        "VL_COLUNAMINIMO": "COLUNAMINIMO",
        "VL_COMPRESSAO": "COMPRESSAO",
        "VL_REFILOLARGURA": "REFILOLARGURA",
        "VL_REFILOCOMPRIMENTO": "REFILOCOMPRIMENTO",
        "VL_MULTLARG": "MULTLARG",
        "VL_MULTCOMP": "MULTCOMP",
        "VL_LARGURAINTERNA": "LARGURAINTERNA",
        "VL_COMPRIMENTOINTERNO": "COMPRIMENTOINTERNO",
        "VL_ALTURAINTERNA_REAL": "ALTURAINTERNA",  # se quiser distinguir da ALTURAINTERNA já usada
        "VL_LARGPECA": "LARGPECA",
        "VL_COMPPECA": "COMPPECA",
        "VL_PACOTESLARGURA": "PACOTESLARGURA",
        "VL_PACOTESCOMPRIMENTO": "PACOTESCOMPRIMENTO",
        "VL_PACOTESALTURA": "PACOTESALTURA",
        "VL_COMPPACOTE": "COMPPACOTE",
        "VL_LARGPACOTE": "LARGPACOTE",
        "VL_ALTURAPACOTE": "ALTURAPACOTE",
        "VL_COMPPALETEFECHADO": "COMPPALETEFECHADO",
        "VL_LARGPALETEFECHADO": "LARGPALETEFECHADO",
        "VL_ALTURAPALETEFECHADO": "ALTURAPALETEFECHADO",
        "VL_AREABRUTAPECACOMREFILOS": "AREABRUTAPECACOMREFILOS",
        "QT_CONSUMOCOR1": "CONSUMOCOR1",
        "QT_CONSUMOCOR2": "CONSUMOCOR2",
        "QT_CONSUMOCOR3": "CONSUMOCOR3",
        "QT_CONSUMOCOR4": "CONSUMOCOR4",
        "VL_VINCOLARG1": "VINCOLARG1",
        "VL_VINCOLARG2": "VINCOLARG2",
        "VL_VINCOLARG3": "VINCOLARG3",
        "VL_VINCOCOMP1": "VINCOCOMP1",
        "VL_VINCOCOMP2": "VINCOCOMP2",
        "VL_VINCOCOMP3": "VINCOCOMP3",
        "VL_VINCOCOMP4": "VINCOCOMP4",
        "VL_VINCOCOMP5": "VINCOCOMP5",
        "VL_LAP": "LAP",
    }

    for dest_col, src_col in num_cols.items():
        data[dest_col] = number(src_col, 0)

    refined = pd.DataFrame(data)

    # Tipagem final
    str_cols = [
        c for c in refined.columns if c.startswith(("ID_", "CD_", "TX_", "FL_", "ST_"))
    ]
    refined[str_cols] = refined[str_cols].astype("string[pyarrow]")
    num_cols_ref = [c for c in refined.columns if c.startswith(("VL_", "QT_"))]
    refined[num_cols_ref] = refined[num_cols_ref].astype(float)
    return refined


def clean_paradas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e padroniza os dados da tabela PARADAS.
    - Aplica prefixos padronizados (CD_, TX_, FL_)
    - Converte flags (Sim/Não, 1/0) para 0/1
    - Normaliza textos
    """
    df = df.copy()
    df.columns = [c.upper() for c in df.columns]
    data: dict[str, pd.Series] = {}

    def varchar(src: str, default: str, name: str) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_varchar(v, default, name))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    def flag(src: str, name: str) -> pd.Series:
        if src not in df.columns:
            return pd.Series([0] * len(df))
        return df[src].apply(
            lambda v: 1 if str(v).strip().lower() in ("sim", "1", "s", "true") else 0
        )

    # Campos principais
    data["CD_PARADA"] = varchar("PARADA", "-1", "CD_PARADA")
    data["TX_DESCRICAO"] = varchar("DESCRICAO", "", "TX_DESCRICAO")

    # Flags
    data["FL_USADACONVERSAO"] = flag("USADACONVERSAO", "FL_USADACONVERSAO")
    data["FL_DESATIVADA"] = flag("DESATIVADA", "FL_DESATIVADA")
    data["FL_EXTERNA"] = flag("FLAGEXTERNA", "FL_EXTERNA")

    refined = pd.DataFrame(data)

    # Tipagem
    str_cols = [c for c in refined.columns if c.startswith(("CD_", "TX_"))]
    refined[str_cols] = refined[str_cols].astype("string[pyarrow]")
    refined[[c for c in refined.columns if c.startswith("FL_")]] = refined[
        [c for c in refined.columns if c.startswith("FL_")]
    ].astype("int8")
    return refined


def clean_maquina(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e padroniza os dados da tabela MAQUINA.
    - Mantém o padrão CD_, TX_, QT_, ID_
    - Corrige nulos, converte numéricos e normaliza strings
    """
    df = df.copy()
    df.columns = [c.upper() for c in df.columns]
    data: dict[str, pd.Series] = {}

    def varchar(src: str, default: str, name: str) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_varchar(v, default, name))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    def number(src: str, default: float) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_number(v, default))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    # Campos
    data["CD_MAQUINA"] = varchar("MAQUINA", "-1", "CD_MAQUINA")
    data["CD_TIPO"] = varchar("TIPO", "-1", "CD_TIPO")
    data["QT_NRDECORES"] = number("NRDECORES", 0)
    data["ID_GRUPOMAQUINA"] = varchar("IDGRUPOMAQUINA", "-1", "ID_GRUPOMAQUINA")

    refined = pd.DataFrame(data)

    # Tipagem
    str_cols = [c for c in refined.columns if c.startswith(("CD_", "ID_"))]
    refined[str_cols] = refined[str_cols].astype("string[pyarrow]")
    refined[["QT_NRDECORES"]] = refined[["QT_NRDECORES"]].astype(float)
    return refined


def clean_itens(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e padroniza os dados da tabela ITENS.

    - Converte colunas numéricas, flags e textos.
    - Aplica prefixos padronizados (CD_, TX_, FL_, VL_, QT_, ST_).
    - Trata NaN, textos "Sim"/"Não" e números inválidos.
    """
    df = df.copy()
    df.columns = [c.upper() for c in df.columns]
    data: dict[str, pd.Series] = {}

    def varchar(src: str, default: str, name: str) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_varchar(v, default, name))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    def number(src: str, default: float) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_number(v, default))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    # Identificadores e textos
    data["CD_ITEM"] = varchar("ITEM", "-1", "CD_ITEM")
    data["CD_TIPOFT2"] = varchar("IDTIPOFT2", "-1", "CD_TIPOFT2")
    data["CD_FAMILIA"] = varchar("IDFAMILIA", "-1", "CD_FAMILIA")
    data["ID_CLIENTE"] = varchar("IDCLIENTE", "-1", "ID_CLIENTE")

    data["ST_ESTADOFT_DETEC"] = varchar("ESTADOFT_DETEC", "", "ST_ESTADOFT_DETEC")
    data["TX_ESTADOFT_DETEC"] = varchar("TEXTOESTADOFT_DETEC", "", "TX_ESTADOFT_DETEC")
    data["ST_STATUSFT"] = varchar("STATUSFT", "", "ST_STATUSFT")
    data["TX_STATUSFT"] = varchar("TEXTOSTATUSFT", "", "TX_STATUSFT")

    data["TX_REFERENCIA"] = varchar("REFERENCIA", "", "TX_REFERENCIA")
    data["CD_REFERENCIA"] = varchar("CODIGOREFERENCIA", "", "CD_REFERENCIA")
    data["TX_TIPOABNT"] = varchar("TIPOABNT", "", "TX_TIPOABNT")
    data["TX_COMPOSICAO"] = varchar("COMPOSICAO", "", "TX_COMPOSICAO")
    data["TX_PATHFIGURADOLASTRO"] = varchar(
        "PATHFIGURADOLASTRO", "", "TX_PATHFIGURADOLASTRO"
    )

    # Flags (booleanos / Sim‑Não)
    if "EXIGELAUDO" in df.columns:
        data["FL_EXIGELAUDO"] = df["EXIGELAUDO"].apply(
            lambda v: 1 if str(v).strip().lower() in ("sim", "1", "s", "true") else 0
        )
    else:
        data["FL_EXIGELAUDO"] = pd.Series([0] * len(df))

    for col in ["REFILADO", "RESINAINTERNA", "AMARRADO", "PALETIZADO"]:
        if col in df.columns:
            data[f"FL_{col.upper()}"] = df[col].apply(
                lambda v: convert_to_varchar(handle_nan(v, 0), "0", f"FL_{col.upper()}")
            )
        else:
            data[f"FL_{col.upper()}"] = pd.Series(["0"] * len(df))

    # Códigos de materiais
    data["CD_ESPELHO"] = varchar("ESPELHO", "-1", "CD_ESPELHO")
    data["CD_FILME"] = varchar("FILME", "-1", "CD_FILME")
    data["CD_FACA"] = varchar("FACA", "-1", "CD_FACA")

    # Cores e consumo
    for i in range(1, 5):
        data[f"TX_COR{i}"] = varchar(f"COR{i}", "", f"TX_COR{i}")
        data[f"VL_CONSUMOCOR{i}"] = number(f"CONSUMOCOR{i}", 0)

    # Numéricos e medidas
    num_map = {
        "VL_GRAMATURA": "GRAMATURA",
        "VL_COLUNAMINIMO": "COLUNAMINIMO",
        "VL_COBBINTMAXIMO": "COBBINTMAXIMO",
        "VL_COMPRESSAO": "COMPRESSAO",
        "VL_LARGURA": "LARGURA",
        "VL_REFILOLARGURA": "REFILOLARGURA",
        "VL_COMPRIMENTO": "COMPRIMENTO",
        "VL_REFILOCOMPRIMENTO": "REFILOCOMPRIMENTO",
        "VL_MULTLARG": "MULTLARG",
        "VL_MULTCOMP": "MULTCOMP",
        "QT_ARRANJO": "ARRANJO",
        "VL_REFUGOCLIENTE": "REFUGOCLIENTE",
        "VL_VINCOLARG1": "VINCOLARG1",
        "VL_VINCOLARG2": "VINCOLARG2",
        "VL_VINCOLARG3": "VINCOLARG3",
        "VL_VINCOCOMP1": "VINCOCOMP1",
        "VL_VINCOCOMP2": "VINCOCOMP2",
        "VL_VINCOCOMP3": "VINCOCOMP3",
        "VL_VINCOCOMP4": "VINCOCOMP4",
        "VL_VINCOCOMP5": "VINCOCOMP5",
        "VL_LAP": "LAP",
        "QT_PROLONGLAP": "PROLONGLAP",
        "VL_LAPNOCOMP": "LAPNOCOMP",
        "VL_LAPINTERNO": "LAPINTERNO",
        "VL_PACOTESLARGURA": "PACOTESLARGURA",
        "VL_PACOTESCOMPRIMENTO": "PACOTESCOMPRIMENTO",
        "VL_PACOTESALTURA": "PACOTESALTURA",
        "QT_PECASPORPACOTE": "PECASPORPACOTE",
        "QT_PECASPORPALETE": "PECASPORPALETE",
        "QT_PACOTESPORPALETE": "PACOTESPORPALETE",
        "QT_UNIDADESPORPALETE": "UNIDADESPORPALETE",
        "VL_LARGURAINTERNA": "LARGURAINTERNA",
        "VL_COMPRIMENTOINTERNO": "COMPRIMENTOINTERNO",
        "VL_ALTURAINTERNA": "ALTURAINTERNA",
        "VL_LARGPECA": "LARGPECA",
        "VL_COMPPECA": "COMPPECA",
        "VL_COMPPACOTE": "COMPPACOTE",
        "VL_LARGPACOTE": "LARGPACOTE",
        "VL_ALTURAPACOTE": "ALTURAPACOTE",
        "VL_COMPPALETEFECHADO": "COMPPALETEFECHADO",
        "VL_LARGPALETEFECHADO": "LARGPALETEFECHADO",
        "VL_ALTURAPALETEFECHADO": "ALTURAPALETEFECHADO",
        "VL_PESOCAIXA": "PESOCAIXA",
        "VL_AREABRUTAPECACOMREFILOS": "AREABRUTAPECACOMREFILOS",
        "VL_AREABRUTAPECA": "AREABRUTAPECA",
        "VL_AREALIQUIDAPECA": "AREALIQUIDAPECA",
        "VL_AREABRUTACHAPA": "AREABRUTACHAPA",
        "VL_AREALIQUIDACHAPA": "AREALIQUIDACHAPA",
        "VL_VOLUMEPALETEFECHADOM3": "VOLUMEPALETEFECHADOM3",
        "VL_VOLUMEPACOTEFECHADOM3": "VOLUMEPACOTEFECHADOM3",
    }
    for dest, src in num_map.items():
        data[dest] = number(src, 0)

    # Quantitativos / contagens
    data["QT_NRCORES"] = number("NRCORES", 0)

    # Palete
    data["CD_PALETE"] = varchar("IDPALETE", "-1", "CD_PALETE")

    refined = pd.DataFrame(data)

    # Tipagem final
    str_cols = [
        c for c in refined.columns if c.startswith(("ID_", "CD_", "TX_", "FL_", "ST_"))
    ]
    refined[str_cols] = refined[str_cols].astype("string[pyarrow]")
    num_cols = [c for c in refined.columns if c.startswith(("VL_", "QT_"))]
    refined[num_cols] = refined[num_cols].astype(float)
    return refined


def clean_facas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e padroniza os dados da tabela FACAS.
    - Aplica prefixos CD_, FL_, VL_
    - Corrige nulos, converte numéricos e normaliza strings
    """
    df = df.copy()
    df.columns = [c.upper() for c in df.columns]
    data: dict[str, pd.Series] = {}

    def varchar(src: str, default: str, name: str) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_varchar(v, default, name))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    def number(src: str, default: float) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_number(v, default))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    def flag(src: str, name: str) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_varchar(handle_nan(v, 0), "0", name))
            if src in df.columns
            else pd.Series(["0"] * len(df))
        )

    # Campos principais
    data["CD_FACA"] = varchar("CODFACA", "-1", "CD_FACA")
    data["CD_STATUS"] = varchar("STATUS", "-1", "CD_STATUS")
    data["VL_COMPLAMINA"] = number("COMPLAMINA", 0)
    data["FL_DESATIVADO"] = flag("DESATIVADOSN", "FL_DESATIVADO")

    refined = pd.DataFrame(data)

    # Tipagem
    str_cols = [c for c in refined.columns if c.startswith(("CD_", "FL_"))]
    refined[str_cols] = refined[str_cols].astype("string[pyarrow]")
    refined[["VL_COMPLAMINA"]] = refined[["VL_COMPLAMINA"]].astype(float)
    return refined


def clean_clientes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e padroniza os dados da tabela CLIENTES.
    - Aplica prefixos ID_, CD_, TX_
    - Corrige nulos e converte tipos
    """
    df = df.copy()
    df.columns = [c.upper() for c in df.columns]
    data: dict[str, pd.Series] = {}

    def varchar(src: str, default: str, name: str) -> pd.Series:
        return (
            df[src].apply(lambda v: convert_to_varchar(v, default, name))
            if src in df.columns
            else pd.Series([default] * len(df))
        )

    # Campos principais
    data["ID_CLIENTE"] = varchar("IDCLIENTE", "-1", "ID_CLIENTE")
    data["TX_CLIENTE"] = varchar("CLIENTE", "", "TX_CLIENTE")
    data["CD_CLIENTE"] = varchar("CODCLIENTE", "-1", "CD_CLIENTE")
    data["CD_REPRESENTANTE"] = varchar("CODREPRESENTANTE", "-1", "CD_REPRESENTANTE")

    refined = pd.DataFrame(data)

    # Tipagem
    str_cols = [c for c in refined.columns if c.startswith(("ID_", "CD_", "TX_"))]
    refined[str_cols] = refined[str_cols].astype("string[pyarrow]")
    return refined
