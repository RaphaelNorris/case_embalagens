# 📦 Case Embalagens - ADAMI Production Optimization

![Lifecycle do Machine Learning](lifecycle_ml.png)

[![CI](https://github.com/RaphaelNorris/case_embalagens/actions/workflows/ci.yml/badge.svg)](https://github.com/RaphaelNorris/case_embalagens/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

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
│   └── workflows/          # CI/CD pipelines
├── project_data_science/   # Projeto principal de Data Science
│   ├── data/
│   │   ├── 01 - raw/      # Dados brutos (Bronze layer)
│   │   ├── 02 - trusted/  # Dados limpos (Silver layer)
│   │   ├── 03 - ml/       # Features para ML
│   │   └── 04 - refined/  # Dados analíticos (Gold layer)
│   ├── docs/              # Documentação do projeto
│   ├── notebooks/         # Jupyter notebooks organizados
│   │   ├── eda/          # Análise exploratória
│   │   │   ├── initial/  # Explorações iniciais
│   │   │   └── refined/  # Análises refinadas
│   │   └── overview/     # Notebooks de visão geral
│   ├── src/              # Código fonte principal
│   │   ├── config.py     # Configuração centralizada
│   │   ├── logger.py     # Logging estruturado
│   │   ├── data/         # Módulos de dados
│   │   │   ├── conn_oracle.py
│   │   │   ├── conn_sql.py
│   │   │   └── data_quality_analytics.py
│   │   ├── features/     # Feature engineering
│   │   │   └── build_features.py
│   │   ├── models/       # Modelos ML
│   │   │   ├── train_model.py
│   │   │   └── predict_model.py
│   │   └── app.py        # Streamlit dashboard
│   ├── tests/            # Testes unitários
│   └── pyproject.toml    # Configuração do projeto
├── project_data_engineer/ # Pipeline de dados (Airflow)
│   └── dags/             # DAGs do Airflow
├── Makefile              # Comandos de automação
├── .pre-commit-config.yaml
└── .env.example          # Template de variáveis de ambiente
```

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

### 4. Dashboard Streamlit

```bash
cd project_data_science/src
streamlit run app.py
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
##.#-iniciais-descrição-data.ipynb
```

Exemplo: `01.0-rn-exploratory-analysis-20240115.ipynb`

### Categorias de Notebooks

- **00-09**: Análise exploratória individual de tabelas
- **10-19**: Análises cruzadas e relacionamentos
- **20-29**: Feature engineering
- **30-39**: Modelagem e experimentação
- **40-49**: Produção e deploy

## 🔍 Qualidade de Código

O projeto utiliza várias ferramentas para garantir qualidade:

- **Ruff**: Linting e formatação rápida (substitui Black, isort, flake8)
- **MyPy**: Type checking estático
- **Pytest**: Framework de testes
- **Pre-commit**: Hooks automáticos antes de commits

## 📚 Documentação

Documentação completa disponível em `project_data_science/docs/`:

- **data_source.md**: Descrição das fontes de dados
- **data_structure.md**: Estrutura das tabelas
- **pipelines.md**: Arquitetura dos pipelines
- **data_quality/**: Relatórios de qualidade de dados

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
