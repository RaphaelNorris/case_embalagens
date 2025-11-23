# 📦 Case Embalagens - ADAMI Production Optimization

![Lifecycle do Machine Learning](docs/images/lifecycle_ml.png)

[![CI](https://github.com/RaphaelNorris/case_embalagens/actions/workflows/ci.yml/badge.svg)](https://github.com/RaphaelNorris/case_embalagens/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **🎯 Status**: Refatoração completa concluída (v2.0.0) - Estrutura modular, documentação completa e boas práticas de engenharia de software para ciência de dados.

## 📋 Visão Geral

Projeto de otimização de processos de produção para ADAMI (indústria de embalagens) em parceria com AMCOM. Implementa um pipeline completo de Machine Learning seguindo metodologias CRISP-DM e CD4ML (Continuous Delivery for Machine Learning).

### Objetivos Principais

- **Análise de Paradas de Máquinas**: Identificar padrões e causas de paradas não programadas
- **Otimização de Produção**: Prever tempo de produção e otimizar alocação de recursos
- **Gestão de Facas/Lâminas**: Monitorar ciclo de vida e performance de ferramentas de corte
- **Analytics em Tempo Real**: Dashboard Streamlit para visualização de KPIs de produção

## 🏗️ Arquitetura do Projeto

```
case_embalagens/
├── .github/
│   └── workflows/              # CI/CD pipelines
├── docs/                       # Documentação e assets
│   └── images/                 # Imagens e diagramas
├── project_data_science/       # 🔬 Projeto principal de Data Science
│   ├── data/                   # Camadas de dados (Medallion Architecture)
│   │   ├── 01 - raw/          # 🥉 Bronze: Dados brutos
│   │   ├── 02 - trusted/      # 🥈 Silver: Dados limpos
│   │   ├── 03 - ml/           # 🤖 Features para ML
│   │   └── 04 - refined/      # 🥇 Gold: Dados analíticos
│   ├── docs/                   # Documentação técnica
│   ├── models/                 # Modelos ML salvos
│   ├── notebooks/              # 📓 Jupyter notebooks organizados
│   │   ├── 01-eda-tables/     # EDA de tabelas individuais (9 notebooks)
│   │   ├── 02-eda-cross/      # Análises cruzadas (3 notebooks)
│   │   ├── 03-preprocessing/  # Pré-processamento (2 notebooks)
│   │   └── 04-production/     # Notebooks de produção (2 notebooks)
│   ├── src/                    # 💻 Código fonte modular
│   │   ├── analysis/          # Processamento e análise
│   │   ├── dashboards/        # 📊 Dashboards Streamlit
│   │   │   ├── components/    # Componentes UI reutilizáveis
│   │   │   ├── dashboard_main.py
│   │   │   └── dashboard_facas.py
│   │   ├── data/              # Conexões e qualidade
│   │   │   ├── conn_oracle.py
│   │   │   ├── conn_sql.py
│   │   │   └── data_quality.py
│   │   ├── features/          # Feature engineering
│   │   ├── models/            # ML (train/predict)
│   │   ├── viz/               # 📈 Visualizações (Plotly)
│   │   ├── config.py          # Configurações (Pydantic)
│   │   └── logger.py          # Logging (Loguru)
│   ├── scripts/                # Scripts utilitários
│   ├── tests/                  # 🧪 Testes unitários
│   └── pyproject.toml          # Configuração do projeto
├── project_data_engineer/      # ⚙️ Pipeline de dados (Airflow)
│   └── dags/                   # 43 DAGs de ETL
│       └── sql/                # Queries SQL (raw/trusted/refined)
├── .env.example                # Template de variáveis
├── .pre-commit-config.yaml     # Hooks de qualidade
├── CHANGELOG.md                # Histórico de mudanças
├── Makefile                    # Comandos de automação
├── PROJECT_STRUCTURE.md        # Estrutura detalhada
└── README.md                   # Este arquivo
```

📖 **Documentação completa**: Cada módulo possui seu próprio README com exemplos e guias de uso.

## 🚀 Quick Start

### Pré-requisitos

- Python 3.10+
- Oracle Client (para conexões Oracle)
- ODBC Driver for SQL Server

### Instalação

```bash
# Clone o repositório
git clone https://github.com/RaphaelNorris/case_embalagens.git
cd case_embalagens

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# Instale dependências de desenvolvimento
make install-dev

# Configure pre-commit hooks
pre-commit install
```

### Uso Rápido

```bash
# Executar testes
make test

# Executar com coverage
make test-cov

# Formatar código
make format

# Executar linting
make lint

# Executar app Streamlit (análise de facas)
make app-facas

# Limpar arquivos temporários
make clean
```

## 📊 Camadas de Dados (Medallion Architecture)

### 🥉 Bronze Layer (01 - raw)
Dados brutos extraídos diretamente das fontes sem transformações.

### 🥈 Silver Layer (02 - trusted)
Dados limpos, padronizados e validados. Principais tabelas:
- `tb_clientes.parquet`: Informações de clientes
- `tb_pedidos.parquet`: Ordens de produção
- `tb_itens.parquet`: Itens dos pedidos
- `tb_maquinas.parquet`: Dados das máquinas
- `tb_facas.parquet`: Informações de facas/lâminas
- `tb_paradas.parquet`: Eventos de parada de máquinas
- `tb_tarefcon.parquet`: Controle de tarefas de produção

### 🥇 Gold Layer (04 - refined)
Dados agregados e prontos para análise/BI.

### 🤖 ML Layer (03 - ml)
Features engineeradas prontas para treinamento de modelos.

## 🔧 Principais Funcionalidades

### 1. Conexões de Banco de Dados

```python
from src.data.conn_oracle import oracle_connection
from src.data.conn_sql import sqlserver_connection

# Oracle (com context manager)
with oracle_connection('trusted') as conn:
    df = pd.read_sql("SELECT * FROM tb_pedidos", conn)

# SQL Server
with sqlserver_connection() as conn:
    df = pd.read_sql("SELECT * FROM dbo.Clientes", conn)
```

### 2. Feature Engineering

```python
from src.features.build_features import (
    create_temporal_features,
    create_production_features,
    create_stoppage_features
)

# Criar features temporais
df = create_temporal_features(df, datetime_col='data_producao')

# Features de produção
df = create_production_features(df, group_cols=['cod_maquina'])

# Features de paradas
df_paradas = create_stoppage_features(df_paradas, df_tarefcon)
```

### 3. Treinamento de Modelos

```python
from src.models.train_model import train_production_model, save_model

# Treinar modelo
model, metrics = train_production_model(
    X, y,
    model_type='random_forest',
    test_size=0.2
)

# Salvar modelo
save_model(model, 'production_optimizer_v1', metadata=metrics)
```

### 4. Dashboards Streamlit

```bash
# Dashboard principal (multi-página)
streamlit run project_data_science/src/dashboards/dashboard_main.py

# Dashboard de facas/lâminas
streamlit run project_data_science/src/dashboards/dashboard_facas.py

# Ou via Makefile
make app-main    # Dashboard principal
make app-facas   # Dashboard de facas
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com coverage
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/test_features.py -v
```

## 📝 Estrutura de Notebooks

Os notebooks seguem a convenção de nomenclatura:

```
##.#-author-description-YYYYMMDD.ipynb
```

Exemplo: `01.0-rn-eda-clientes-20240101.ipynb`

### Categorias de Notebooks

- **📊 01-eda-tables/** (9 notebooks): Análise exploratória de tabelas individuais
  - Clientes, Pedidos, Itens, Máquinas, Facas, Paradas, Tarefcon
  - Metodologia: Load → Describe → Quality → Visualize → Insights

- **🔗 02-eda-cross/** (3 notebooks): Análises cruzadas entre tabelas
  - Relacionamentos pedidos-itens, tarefcon-paradas, tarefcon-itens
  - Validação de integridade referencial

- **🧹 03-preprocessing/** (2 notebooks): Pré-processamento e limpeza
  - Pipeline de transformação Raw → Trusted → Refined
  - Tratamento de outliers, missing values, tipos

- **🚀 04-production/** (2 notebooks): Notebooks prontos para produção
  - Overview piloto e associação temporal
  - Integração com Airflow

📚 **Cada categoria possui seu próprio README** com documentação detalhada.

## 🔍 Qualidade de Código

O projeto utiliza várias ferramentas para garantir qualidade:

- **Ruff**: Linting e formatação rápida (substitui Black, isort, flake8)
- **MyPy**: Type checking estático
- **Pytest**: Framework de testes
- **Pre-commit**: Hooks automáticos antes de commits

## 📚 Documentação

### Documentação por Módulo

Cada módulo possui documentação detalhada com exemplos práticos:

- **[src/README.md](project_data_science/src/README.md)**: Visão geral de todos os módulos
- **[src/data/README.md](project_data_science/src/data/README.md)**: Conexões e qualidade de dados
- **[src/features/README.md](project_data_science/src/features/README.md)**: Feature engineering
- **[src/models/README.md](project_data_science/src/models/README.md)**: Treinamento e predição
- **[src/viz/README.md](project_data_science/src/viz/README.md)**: Visualizações Plotly
- **[src/analysis/README.md](project_data_science/src/analysis/README.md)**: Processamento de dados
- **[src/dashboards/README.md](project_data_science/src/dashboards/README.md)**: Dashboards Streamlit

### Documentação de Dados

- **[data/README.md](project_data_science/data/README.md)**: Medallion Architecture (Bronze/Silver/Gold)
- **[data/01 - raw/README.md](project_data_science/data/01%20-%20raw/README.md)**: Camada Bronze
- **[data/02 - trusted/README.md](project_data_science/data/02%20-%20trusted/README.md)**: Camada Silver
- **[data/03 - ml/README.md](project_data_science/data/03%20-%20ml/README.md)**: Features ML
- **[data/04 - refined/README.md](project_data_science/data/04%20-%20refined/README.md)**: Camada Gold

### Documentação de Notebooks

- **[notebooks/01-eda-tables/README.md](project_data_science/notebooks/01-eda-tables/README.md)**: EDA de tabelas
- **[notebooks/02-eda-cross/README.md](project_data_science/notebooks/02-eda-cross/README.md)**: Análises cruzadas
- **[notebooks/03-preprocessing/README.md](project_data_science/notebooks/03-preprocessing/README.md)**: Pré-processamento
- **[notebooks/04-production/README.md](project_data_science/notebooks/04-production/README.md)**: Produção

### Documentação Técnica

- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**: Estrutura completa do projeto
- **[CHANGELOG.md](CHANGELOG.md)**: Histórico de mudanças
- **docs/**: Fontes de dados, estrutura, pipelines, relatórios de qualidade

## 🔐 Segurança

- ✅ Credenciais gerenciadas via variáveis de ambiente (.env)
- ✅ `.gitignore` configurado para não commitar dados sensíveis
- ✅ Pre-commit hook para detecção de secrets
- ✅ Validação de dados com Pydantic

## 🛠️ Stack Tecnológica

### Data & ML
- **Pandas, NumPy**: Manipulação de dados
- **Scikit-learn, XGBoost, LightGBM**: Machine Learning
- **Streamlit**: Dashboards interativos

### Databases
- **Oracle DB**: Banco de dados principal
- **SQL Server**: Analytics e BI

### DevOps & Tools
- **Airflow**: Orquestração de pipelines
- **GitHub Actions**: CI/CD
- **Pre-commit**: Hooks de qualidade
- **Ruff**: Linting/formatação
- **Pytest**: Testing

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Convenções de Código

- Seguir PEP 8 (automaticamente via Ruff)
- Type hints em todas as funções públicas
- Docstrings no formato Google
- Testes para novas funcionalidades

## 📄 Licença

Este projeto é propriedade de ADAMI em parceria com AMCOM.

## 👥 Autores

- **Raphael Norris** - *Data Science Lead*

## 🙏 Agradecimentos

- ADAMI - Por fornecer os dados e expertise de domínio
- AMCOM - Parceria tecnológica

---

**Desenvolvido com ❤️ para otimização de processos industriais**
