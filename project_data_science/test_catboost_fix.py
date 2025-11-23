#!/usr/bin/env python3
"""
Teste rápido para verificar se a correção do CatBoost funcionou
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Configurar paths
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

print(f"✓ Projeto: {PROJECT_ROOT}")
print(f"✓ Source: {SRC_DIR}")

try:
    from pipelines.DS.pipelines import run_pipeline
    print("✓ Import do pipeline realizado com sucesso")
except ImportError as e:
    print(f"❌ Erro no import: {e}")
    sys.exit(1)

# Configurações de teste
MACHINE_TYPE = 'flexo'
MODEL_TYPE = 'catboost'
TASK_TYPE = 'regression'
RANDOM_STATE = 42
CLASSIFICATION_THRESHOLD = 0.7

print(f"\nTestando configuração:")
print(f"  - Máquina: {MACHINE_TYPE}")
print(f"  - Modelo: {MODEL_TYPE}")
print(f"  - Tarefa: {TASK_TYPE}")

try:
    results = run_pipeline(
        machine_type=MACHINE_TYPE,
        task_type=TASK_TYPE,
        model_type=MODEL_TYPE,
        random_state=RANDOM_STATE,
        shap_sample_size=0,  # Desabilitar SHAP para regressão
        classification_threshold=CLASSIFICATION_THRESHOLD,
    )
    print("✅ Pipeline executado com sucesso!")
    
    # Exibir métricas
    metrics = results['metrics']
    print("\nMétricas do modelo:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
            
    print(f"\nShape do dataset: {results['df'].shape}")
    print(f"Features selecionadas: {len(results.get('selected_features', []))}")
    
except Exception as e:
    print(f"❌ Erro na execução do pipeline: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 Teste concluído com sucesso!")