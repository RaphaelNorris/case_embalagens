#!/bin/bash

# Script para executar o aplicativo Streamlit

echo "🏭 Iniciando Preditor de Produtividade Industrial..."
echo ""

# Ativar ambiente virtual se existir
if [ -d "env" ]; then
    echo "✓ Ativando ambiente virtual..."
    source env/bin/activate
fi

# Executar Streamlit
echo "✓ Iniciando Streamlit..."
streamlit run src/app/streamlit_app.py
