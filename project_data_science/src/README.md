# 🔧 Source Code (`src/`)

## Propósito
Código-fonte modular e reutilizável do projeto de ciência de dados.

---

## 📁 Estrutura de Módulos

```
src/
├── 📊 dashboards/          # Dashboards interativos (Streamlit)
├── 🔌 data/                # Conexões e qualidade de dados
├── 🔬 analysis/            # Processamento e análise
├── 🛠️ features/            # Feature engineering
├── 🤖 models/              # Treinamento e predição ML
├── 📈 viz/                 # Visualizações (Plotly)
├── ⚙️ config.py            # Configurações centralizadas
└── 📝 logger.py            # Sistema de logging
```

---

## 🗺️ Visão Geral dos Módulos

### 📊 [dashboards/](./dashboards/)
**Aplicações web interativas** para visualização e análise.

**Principais arquivos:**
- `dashboard_main.py` - Dashboard multi-página principal
- `dashboard_facas.py` - Dashboard especializado em facas
- `components/ui.py` - Componentes UI reutilizáveis

**Uso:**
```bash
make app-main    # Dashboard principal
make app-facas   # Dashboard de facas
```

[📖 Documentação completa →](./dashboards/README.md)

---

### 🔌 [data/](./data/)
**Gerenciamento de conexões** com bancos de dados e **qualidade de dados**.

**Principais arquivos:**
- `conn_oracle.py` - Conexões Oracle (Bronze/Silver/Gold)
- `conn_sql.py` - Conexões SQL Server
- `data_quality.py` - Validação e monitoramento

**Uso:**
```python
from src.data.conn_oracle import oracle_connection

with oracle_connection('trusted') as conn:
    df = pd.read_sql("SELECT * FROM tb_clientes", conn)
```

[📖 Documentação completa →](./data/README.md)

---

### 🔬 [analysis/](./analysis/)
**Processamento e análise** de dados para limpeza e transformação.

**Principais arquivos:**
- `data_processing.py` - Utilitários de transformação

**Funções principais:**
- `clean_numeric_and_categorical()` - Limpeza automática
- `calculate_differences()` - Comparação entre datasets
- `create_temporal_aggregation()` - Agregações temporais
- `abc_classification()` - Análise de Pareto

**Uso:**
```python
from src.analysis.data_processing import clean_numeric_and_categorical

df_clean, num_cols, cat_cols = clean_numeric_and_categorical(df_raw)
```

[📖 Documentação completa →](./analysis/README.md)

---

### 🛠️ [features/](./features/)
**Feature engineering** para modelos de Machine Learning.

**Principais arquivos:**
- `build_features.py` - Criação de features

**Funções principais:**
- `create_temporal_features()` - Features de data/hora
- `create_production_features()` - Rolling stats e lags
- `create_stoppage_features()` - Análise de paradas
- `merge_temporal_production_data()` - Merge temporal

**Uso:**
```python
from src.features.build_features import create_temporal_features, create_production_features

df = create_temporal_features(df, 'dt_inicio')
df = create_production_features(df, group_cols=['cod_maquina'])
```

[📖 Documentação completa →](./features/README.md)

---

### 📈 [viz/](./viz/)
**Visualizações interativas** usando Plotly.

**Principais arquivos:**
- `plots.py` - Biblioteca de gráficos

**Funções principais:**
- `plot_time_series()` - Séries temporais
- `plot_box_by_category()` - Box plots
- `plot_pareto()` - Análise ABC
- `plot_histogram()` - Histogramas
- `plot_3d_scatter()` - Scatter 3D

**Uso:**
```python
from src.viz.plots import plot_time_series, plot_pareto

fig = plot_time_series(df, x_col='dt_inicio', y_col='quantidade', title='Produção')
fig.show()
```

[📖 Documentação completa →](./viz/README.md)

---

## ⚙️ Configuração Global

### `config.py`
Configurações centralizadas usando **Pydantic**.

**Classes:**
- `OracleConfig` - Conexões Oracle
- `SQLServerConfig` - Conexões SQL Server
- `DataPathsConfig` - Caminhos de dados
- `MLConfig` - Configurações de ML
- `AppConfig` - Configuração geral

**Uso:**
```python
from src.config import get_config

config = get_config()
print(config.oracle.raw.user)
print(config.data_paths.raw)
```

**Configuração via `.env`:**
```bash
# Oracle
ORACLE_RAW_USER=user
ORACLE_RAW_PASSWORD=pass
ORACLE_RAW_DSN=host:1521/service

# Paths
DATA_PATH_RAW=data/01 - raw
DATA_PATH_TRUSTED=data/02 - trusted
```

---

## 📝 Logging

### `logger.py`
Sistema de logging usando **Loguru**.

**Features:**
- Logs estruturados (JSON em produção)
- Rotação automática de arquivos
- Níveis configuráveis (DEBUG, INFO, WARNING, ERROR)

**Uso:**
```python
from src.logger import logger

logger.info("Iniciando processamento...")
logger.warning(f"Encontrados {n} valores nulos")
logger.error("Falha na conexão", exc_info=True)
```

**Níveis de log:**
- `DEBUG` - Detalhes técnicos (desenvolvimento)
- `INFO` - Informações gerais (progresso)
- `WARNING` - Avisos (não crítico)
- `ERROR` - Erros (falhas recuperáveis)
- `CRITICAL` - Erros críticos (falhas fatais)

---

## 🔄 Fluxo de Dados

### Pipeline Típico:

1. **Extração** (`data/`)
   ```python
   from src.data.conn_oracle import oracle_connection

   with oracle_connection('raw') as conn:
       df = pd.read_sql("SELECT * FROM tb_tarefcon", conn)
   ```

2. **Limpeza** (`analysis/`)
   ```python
   from src.analysis.data_processing import clean_numeric_and_categorical

   df_clean, num_cols, cat_cols = clean_numeric_and_categorical(df)
   ```

3. **Feature Engineering** (`features/`)
   ```python
   from src.features.build_features import create_temporal_features

   df_features = create_temporal_features(df_clean, 'dt_inicio')
   ```

4. **Modelagem** (`models/`)
   ```python
   from src.models.train_model import train_production_model

   model, metrics = train_production_model(X, y, model_type='xgboost')
   ```

5. **Visualização** (`viz/`)
   ```python
   from src.viz.plots import plot_time_series

   fig = plot_time_series(df, 'dt_inicio', 'quantidade', 'Produção')
   ```

6. **Dashboard** (`dashboards/`)
   ```python
   streamlit run src/dashboards/dashboard_main.py
   ```

---

## 🧪 Testes

```
tests/
├── unit/              # Testes unitários por módulo
│   ├── test_data.py
│   ├── test_features.py
│   └── test_catboost_fix.py
├── integration/       # Testes de integração
└── dashboards/        # Testes de dashboards
```

**Executar testes:**
```bash
make test              # Todos os testes
pytest tests/unit/     # Apenas unitários
pytest -v              # Verbose
pytest -k "test_oracle"  # Filtrar por nome
```

---

## 📚 Convenções de Código

### Imports
```python
# 1. Standard library
import os
from pathlib import Path

# 2. Third-party
import pandas as pd
import numpy as np

# 3. Local
from src.config import get_config
from src.logger import logger
```

### Docstrings (Google Style)
```python
def calculate_metric(df: pd.DataFrame, column: str) -> float:
    """Calcula métrica agregada de uma coluna.

    Args:
        df: DataFrame com os dados
        column: Nome da coluna para calcular

    Returns:
        Valor da métrica calculada

    Raises:
        KeyError: Se coluna não existir
        ValueError: Se coluna não for numérica
    """
    return df[column].mean()
```

### Type Hints
```python
from typing import List, Dict, Tuple, Optional

def process_data(
    df: pd.DataFrame,
    columns: List[str],
    threshold: Optional[float] = None
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    ...
```

---

## 🛠️ Ferramentas de Desenvolvimento

### Linting e Formatação
```bash
make format    # Ruff format (Black-compatible)
make lint      # Ruff linting
make type      # MyPy type checking
```

### Pre-commit Hooks
```bash
pre-commit install              # Instalar hooks
pre-commit run --all-files      # Rodar manualmente
```

**Hooks configurados:**
- ✅ Ruff (linting + formatting)
- ✅ MyPy (type checking)
- ✅ Trailing whitespace
- ✅ YAML/JSON validation
- ✅ Secrets detection

---

## 🚀 Quick Start

### 1. Configurar ambiente
```bash
# Instalar dependências
make install-dev

# Configurar variáveis
cp .env.example .env
# Editar .env com suas credenciais
```

### 2. Testar conexões
```python
from src.data.conn_oracle import oracle_connection

with oracle_connection('trusted') as conn:
    df = pd.read_sql("SELECT COUNT(*) FROM tb_clientes", conn)
    print(f"✅ {df.iloc[0, 0]} clientes")
```

### 3. Executar pipeline
```bash
# Extrair dados
python scripts/data_extraction/extract_oracle.py

# Processar
python scripts/analysis/process_data.py

# Treinar modelo
python scripts/ml/train_models.py

# Visualizar
streamlit run src/dashboards/dashboard_main.py
```

---

## 📖 Documentação Adicional

- [📊 Dashboards](./dashboards/README.md)
- [🔌 Data](./data/README.md)
- [🔬 Analysis](./analysis/README.md)
- [🛠️ Features](./features/README.md)
- [🤖 Models](./models/README.md)
- [📈 Viz](./viz/README.md)

---

## 🤝 Contribuindo

1. Seguir convenções de código
2. Adicionar type hints
3. Documentar funções (docstrings)
4. Escrever testes
5. Rodar `make format lint` antes de commitar
6. Atualizar documentação se necessário

---

## ❓ Troubleshooting

### Erro: `ModuleNotFoundError: No module named 'src'`
**Solução:** Executar a partir da raiz do projeto ou adicionar ao PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:/home/user/case_embalagens/project_data_science"
```

### Erro: `Config file not found`
**Solução:** Criar `.env` a partir do `.env.example`

### Performance lenta
**Solução:**
- Usar caching (`@functools.lru_cache`)
- Processar em chunks
- Salvar intermediários em Parquet
- Usar `.query()` ao invés de indexação booleana
