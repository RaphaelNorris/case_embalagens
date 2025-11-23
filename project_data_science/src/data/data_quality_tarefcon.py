import pandas as pd
from datetime import datetime
import numpy as np

def handle_nan(value, nan_value):
    if pd.isna(value):
        return nan_value
    if isinstance(value, str) and value.strip() == "":
        return nan_value
    
    return value

def convert_to_varchar(value, nan_value, field_name=None):
    if field_name and field_name.startswith('FL_'):
        # Campos booleanos (0/1)
        if pd.isna(value):
            return "0"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (int, float)):
            return "1" if value != 0 else "0"
        if isinstance(value, str):
            v = value.strip().upper()
            if v in ("1", "Y", "S", "TRUE", "T", "SIM"):
                return "1"
            if v in ("0", "N", "FALSE", "F", "NAO", "NÃO"):
                return "0"
            return "1" if v else "0"
        return "1" if bool(value) else "0"

    elif field_name and field_name.startswith('TX_'):
        # Campos texto (não podem ser None)
        if pd.isna(value):
            return " "
        if isinstance(value, str):
            return value.strip() or ""
        return str(value).strip() or ""
    
    else:
        # Outros VARCHAR
        if pd.isna(value):
            return nan_value
        if isinstance(value, str):
            return value.strip() or nan_value
        return str(value).strip() or nan_value
    
def convert_to_timestamp(value, nan_date=None):
    if pd.isna(value):
        return datetime(2999, 1, 1) if nan_date == "2999/01/01" else pd.NaT
    if isinstance(value, datetime):
        return value
    for fmt in [
        "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S", "%d/%m/%y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f"
    ]:
        try:
            return datetime.strptime(str(value), fmt)
        except Exception:
            continue
    try:
        return pd.to_datetime(value, errors="coerce") or (
            datetime(2999, 1, 1) if nan_date == "2999/01/01" else pd.NaT
        )
    except Exception:
        return datetime(2999, 1, 1) if nan_date == "2999/01/01" else pd.NaT

def convert_to_number(value, nan_value):
    if pd.isna(value):
        return nan_value
    try:
        return float(value) if "." in str(value) else int(value)
    except Exception:
        return nan_value

# -----------------------------
# aplica no DataFrame
# -----------------------------
def clean_tarefcon(df):
    df = df.copy()
    df["ID_MAQUINA"]           = df["ID_MAQUINA"].apply(lambda v: convert_to_varchar(v, "-1", "ID_MAQUINA"))
    df["FL_PARADA"]            = df["FL_PARADA"].apply(lambda v: convert_to_varchar(handle_nan(v, 0), "0", "FL_PARADA"))
    df["CD_PARADAOUCONV"]      = df["CD_PARADAOUCONV"].apply(lambda v: convert_to_varchar(v, "-1", "CD_PARADAOUCONV"))
    df["TX_TURMA"]             = df["TX_TURMA"].apply(lambda v: convert_to_varchar(v, "", "TX_TURMA"))
    df["TX_OP"]                = df["TX_OP"].apply(lambda v: convert_to_varchar(v, "", "TX_OP"))
    df["ID_PEDIDO"]            = df["ID_PEDIDO"].apply(lambda v: convert_to_varchar(v, "-1", "ID_PEDIDO"))
    df["ID_ITEM"]              = df["ID_ITEM"].apply(lambda v: convert_to_varchar(v, "-1", "ID_ITEM"))
    df["VL_REPROGRAMACAO"]     = df["VL_REPROGRAMACAO"].apply(lambda v: convert_to_number(v, 0))
    df["QT_ARRANJO"]           = df["QT_ARRANJO"].apply(lambda v: convert_to_number(v, 0))
    df["VL_GRAMATURA"]         = df["VL_GRAMATURA"].apply(lambda v: convert_to_number(v, 0))
    df["QT_PROGRAMADA"]        = df["QT_PROGRAMADA"].apply(lambda v: convert_to_number(v, 0))
    df["VL_CHAPASALIMENTADAS"] = df["VL_CHAPASALIMENTADAS"].apply(lambda v: convert_to_number(v, 0))
    df["QT_PRODUZIDA"]         = df["QT_PRODUZIDA"].apply(lambda v: convert_to_number(v, 0))
    df["QT_AJUSTE"]            = df["QT_AJUSTE"].apply(lambda v: convert_to_number(v, 0))
    df["VL_DURACAOPREVISTA"]   = df["VL_DURACAOPREVISTA"].apply(lambda v: convert_to_number(v, 0))
    df["DT_INICIO"]            = df["DT_INICIO"].apply(lambda v: convert_to_timestamp(v, "2999/01/01"))
    df["DT_FIM"]               = df["DT_FIM"].apply(lambda v: convert_to_timestamp(v, "2999/01/01"))
    df["DT_DIADATURMA"]        = df["DT_DIADATURMA"].apply(lambda v: convert_to_timestamp(v, "2999/01/01"))
    df["ID_CLIENTE"]           = df["ID_CLIENTE"].apply(lambda v: convert_to_varchar(v, "-1", "ID_CLIENTE"))
    df["ID_USUARIO"]           = df["ID_USUARIO"].apply(lambda v: convert_to_varchar(v, "-1", "ID_USUARIO"))
    df["VL_ORIGEMREGISTRO"]    = df["VL_ORIGEMREGISTRO"].apply(lambda v: convert_to_number(v, 0))
    df["TX_DESCORIGEMREGISTRO"]= df["TX_DESCORIGEMREGISTRO"].apply(lambda v: convert_to_varchar(v, "", "TX_DESCORIGEMREGISTRO"))
    df["FL_SKIPFEED"]          = df["FL_SKIPFEED"].apply(lambda v: convert_to_varchar(handle_nan(v, 0), "0", "FL_SKIPFEED"))
    df["TX_OPONDULADA"]        = df["TX_OPONDULADA"].apply(lambda v: convert_to_varchar(v, "", "TX_OPONDULADA"))
    df["VL_DURACAO"]           = df["VL_DURACAO"].apply(lambda v: convert_to_number(v, 0))
    df["CD_FACA"]              = df["CD_FACA"].apply(lambda v: convert_to_varchar(v, "-1", "CD_FACA"))
    return df