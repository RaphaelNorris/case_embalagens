"""
Streamlit App Configuration
==========================

Configuration settings for the Streamlit application.
"""

from pathlib import Path

# App settings
APP_TITLE = "Production Productivity Predictor"
APP_ICON = "🏭"

# Model settings
MODEL_DIR = Path("models")
SUPPORTED_MACHINE_TYPES = ["flexo", "cv"]

# UI settings
MACHINE_TYPE_LABELS = {
    "flexo": "Flexografia",
    "cv": "Corte e Vinco"
}

# Default values for form inputs
DEFAULT_VALUES = {
    "flexo": {
        "CD_PEDIDO": 12345,
        "CD_ITEM": 1,
        "CD_FACA": "F001",
        "VL_COMPRIMENTO": 800.0,
        "VL_LARGURA": 600.0,
        "VL_GRAMATURA": 250.0,
        "QT_NRCORES": 4,
        "VL_COMPRIMENTOINTERNO": 780.0,
        "VL_LARGURAINTERNA": 580.0,
        "VL_ALTURAINTERNA": 150.0,
        "QT_ARRANJO": 2,
        "VL_MULTCOMP": 2,
        "VL_MULTLARG": 3,
        "QT_PEDIDA": 1000,
        "FL_TESTE_EXIGELAUDO": 0,
        "CAT_COMPOSICAO": "KRAFT",
        "TX_TIPOABNT": "TIPO_A"
    },
    "cv": {
        "CD_PEDIDO": 67890,
        "CD_ITEM": 1,
        "CD_FACA": "C001",
        "VL_COMPRIMENTO": 400.0,
        "VL_LARGURA": 300.0,
        "VL_GRAMATURA": 180.0,
        "QT_NRCORES": 2,
        "VL_COMPRIMENTOINTERNO": 380.0,
        "VL_LARGURAINTERNA": 280.0,
        "VL_ALTURAINTERNA": 100.0,
        "QT_ARRANJO": 1,
        "VL_MULTCOMP": 4,
        "VL_MULTLARG": 5,
        "QT_PEDIDA": 2000,
        "FL_TESTE_EXIGELAUDO": 1,
        "CAT_COMPOSICAO": "DUPLEX",
        "TX_TIPOABNT": "TIPO_B"
    }
}

# Feature descriptions for tooltips
FEATURE_DESCRIPTIONS = {
    "CD_PEDIDO": "Código único do pedido",
    "CD_ITEM": "Código do item dentro do pedido",
    "CD_FACA": "Código da faca utilizada na produção",
    "VL_COMPRIMENTO": "Comprimento da peça em milímetros",
    "VL_LARGURA": "Largura da peça em milímetros",
    "VL_GRAMATURA": "Gramatura do material em g/m²",
    "QT_NRCORES": "Número de cores na impressão",
    "VL_COMPRIMENTOINTERNO": "Comprimento interno da caixa em mm",
    "VL_LARGURAINTERNA": "Largura interna da caixa em mm",
    "VL_ALTURAINTERNA": "Altura interna da caixa em mm",
    "QT_ARRANJO": "Número de arranjos na produção",
    "VL_MULTCOMP": "Multiplicador de comprimento",
    "VL_MULTLARG": "Multiplicador de largura",
    "QT_PEDIDA": "Quantidade total pedida",
    "FL_TESTE_EXIGELAUDO": "Indica se exige laudo de teste",
    "CAT_COMPOSICAO": "Tipo de composição do material",
    "TX_TIPOABNT": "Tipo ABNT do material"
}
