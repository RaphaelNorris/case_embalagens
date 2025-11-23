# 🏗️ Estrutura do Projeto - Case Embalagens ADAMI

> Última atualização: 2024-11-23
> Versão: 2.0.0 (Refatoração completa)

## 📂 Estrutura de Diretórios

```
case_embalagens/
├── .github/
│   └── workflows/
│       └── ci.yml                          # CI/CD pipeline
├── project_data_science/                   # 🔬 Projeto de Data Science
│   ├── data/                               # Dados (medallion architecture)
│   │   ├── 01 - raw/                      # Bronze: dados brutos
│   │   ├── 02 - trusted/                  # Silver: dados limpos
│   │   ├── 03 - ml/                       # Features para ML
│   │   └── 04 - refined/                  # Gold: dados analíticos
│   ├── docs/                               # Documentação do projeto
│   │   ├── data_quality/                  # Relatórios de qualidade
│   │   ├── analise/                       # Análises documentadas
│   │   ├── data_source.md                 # Fontes de dados
│   │   ├── data_structure.md              # Estrutura de dados
│   │   └── pipelines.md                   # Arquitetura de pipelines
│   ├── models/                             # Modelos ML treinados
│   ├── notebooks/                          # 📓 Jupyter Notebooks ORGANIZADOS
│   │   ├── 01-eda-tables/                 # EDA de tabelas individuais
│   │   │   ├── 00.0-rn-metadata-column-names-20240101.ipynb
│   │   │   ├── 01.0-rn-eda-general-20240101.ipynb
│   │   │   ├── 02.0-rn-eda-clientes-20240101.ipynb
│   │   │   ├── 03.0-rn-eda-facas-20240101.ipynb
│   │   │   ├── 04.0-rn-eda-maquinas-20240101.ipynb
│   │   │   ├── 05.0-rn-eda-itens-20240101.ipynb
│   │   │   ├── 06.0-rn-eda-pedidos-20240101.ipynb
│   │   │   ├── 07.0-rn-eda-paradas-20240101.ipynb
│   │   │   └── 08.0-rn-eda-tarefcon-20240101.ipynb
│   │   ├── 02-eda-cross/                  # Análises cruzadas
│   │   │   ├── 10.0-rn-cross-pedidos-itens-20240101.ipynb
│   │   │   ├── 11.0-rn-cross-tarefcon-paradas-20240101.ipynb
│   │   │   └── 12.0-rn-cross-tarefcon-itens-20240101.ipynb
│   │   ├── 03-preprocessing/              # Pré-processamento
│   │   │   ├── 20.0-rn-preprocessing-refined-20240101.ipynb
│   │   │   └── 20.1-rn-preprocessing-tables-20240101.ipynb
│   │   ├── 04-production/                 # Notebooks de produção
│   │   │   ├── 00.0-rn-overview-pilot-20240101.ipynb
│   │   │   └── 30.0-rn-production-temporal-association-20240101.ipynb
│   │   └── NOTEBOOK_RENAMING_MAP.md       # Mapa de renomeação
│   ├── src/                                # 💻 Código fonte modular
│   │   ├── analysis/                      # Módulos de análise
│   │   │   ├── __init__.py
│   │   │   └── data_processing.py        # Processamento e transformação
│   │   ├── dashboards/                    # 📊 Dashboards Streamlit
│   │   │   ├── components/                # Componentes reutilizáveis
│   │   │   │   ├── __init__.py
│   │   │   │   └── ui.py                  # Componentes de UI
│   │   │   ├── pages/                     # Páginas do dashboard
│   │   │   ├── utils/                     # Utilidades dos dashboards
│   │   │   ├── dashboard_facas.py         # Dashboard de facas/lâminas
│   │   │   └── dashboard_main.py          # Dashboard principal
│   │   ├── data/                          # Módulos de dados
│   │   │   ├── __init__.py
│   │   │   ├── conn_oracle.py            # Conexão Oracle
│   │   │   ├── conn_sql.py               # Conexão SQL Server
│   │   │   ├── data_quality_analytics.py # Qualidade de dados
│   │   │   └── data_treatment.py         # Tratamento de dados
│   │   ├── features/                      # Feature engineering
│   │   │   ├── __init__.py
│   │   │   └── build_features.py         # Construção de features
│   │   ├── models/                        # Módulos de ML
│   │   │   ├── __init__.py
│   │   │   ├── train_model.py            # Treinamento
│   │   │   └── predict_model.py          # Predição
│   │   ├── viz/                           # 📈 Visualizações
│   │   │   ├── __init__.py
│   │   │   └── plots.py                  # Funções de plotagem
│   │   ├── config.py                      # Configuração centralizada
│   │   └── logger.py                      # Logging estruturado
│   ├── tests/                             # 🧪 Testes unitários
│   │   ├── test_config.py
│   │   ├── test_features.py
│   │   └── test_models.py
│   └── pyproject.toml                     # Configuração do projeto
├── project_data_engineer/                 # ⚙️ Pipeline de dados (Airflow)
│   ├── dags/                              # DAGs do Airflow
│   │   ├── sql/                           # Queries SQL
│   │   │   ├── raw/                       # Queries para camada raw
│   │   │   ├── trusted/                   # Queries para camada trusted
│   │   │   └── refined/                   # Queries para camada refined
│   │   └── *.py                          # 44 DAGs de ETL
│   └── airflow.cfg                        # Configuração do Airflow
├── .gitignore                             # Git ignore rules
├── .pre-commit-config.yaml                # Pre-commit hooks
├── .env.example                           # Template de variáveis de ambiente
├── CHANGELOG.md                           # Registro de mudanças
├── Makefile                               # Comandos de automação
├── PROJECT_STRUCTURE.md                   # Este arquivo
└── README.md                              # Documentação principal
```

## 📋 Convenção de Nomenclatura de Notebooks

Todos os notebooks seguem o padrão:

```
##.#-author-description-YYYYMMDD.ipynb
```

**Exemplo**: `01.0-rn-eda-clientes-20240101.ipynb`

- `##.#`: Número sequencial com subcategoria
- `author`: Iniciais do autor (rn = Raphael Norris)
- `description`: Descrição curta do conteúdo
- `YYYYMMDD`: Data de criação

### Categorias de Notebooks

| Faixa | Categoria | Descrição |
|-------|-----------|-----------|
| 00-09 | EDA Tabelas | Análise exploratória de tabelas individuais |
| 10-19 | EDA Cross | Análises cruzadas entre tabelas |
| 20-29 | Preprocessing | Pré-processamento e limpeza |
| 30-39 | Production | Notebooks de produção/deploy |
| 40-49 | Modeling | Modelagem e experimentação ML |
| 50-59 | Evaluation | Avaliação de modelos |

## 🎯 Módulos Principais

### 1. **src/data/**
Módulos para conexão e manipulação de dados:
- `conn_oracle.py`: Conexão com Oracle (RAW/TRUSTED/REFINED)
- `conn_sql.py`: Conexão com SQL Server
- `data_quality_analytics.py`: Análise de qualidade
- `data_treatment.py`: Tratamento de dados

### 2. **src/features/**
Feature engineering:
- `build_features.py`: Features temporais, produção, paradas, facas

### 3. **src/models/**
Machine Learning:
- `train_model.py`: Treina modelos (RF, XGBoost, LightGBM)
- `predict_model.py`: Predições com intervalos de confiança

### 4. **src/analysis/**
Análise de dados:
- `data_processing.py`: Processamento, agregações, ABC

### 5. **src/viz/**
Visualizações:
- `plots.py`: Gráficos reutilizáveis (Plotly)

### 6. **src/dashboards/**
Dashboards interativos:
- `dashboard_facas.py`: Análise de facas/lâminas
- `dashboard_main.py`: Dashboard principal multi-página
- `components/ui.py`: Componentes de UI reutilizáveis

## 🔧 Comandos Make Úteis

```bash
make install-dev     # Instalar dependências de desenvolvimento
make test           # Executar testes
make test-cov       # Testes com coverage
make format         # Formatar código
make lint           # Linting
make clean          # Limpar arquivos temporários
```

## 📊 Arquitetura de Dados (Medallion)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌───────────┐
│   🥉 Raw    │────▶│  🥈 Trusted  │────▶│  🤖 ML      │────▶│  🥇 Gold  │
│  (Bronze)   │     │   (Silver)   │     │  Features   │     │ (Refined) │
└─────────────┘     └──────────────┘     └─────────────┘     └───────────┘
  Dados brutos       Limpo/validado      Engineered          Analítico
```

## 🏃 Como Executar

### Dashboards
```bash
# Dashboard de Facas
cd project_data_science/src/dashboards
streamlit run dashboard_facas.py

# Dashboard Principal
streamlit run dashboard_main.py
```

### Notebooks
```bash
cd project_data_science/notebooks
jupyter lab
```

### Testes
```bash
cd project_data_science
pytest tests/ -v
```

## 📝 Melhorias Implementadas

✅ **Estrutura Modular**: Código organizado em módulos reutilizáveis
✅ **Convenção de Nomenclatura**: Notebooks seguem padrão consistente
✅ **Organização por Categoria**: Notebooks agrupados logicamente
✅ **Componentes Reutilizáveis**: UI, plots, análises modularizadas
✅ **Configuração Centralizada**: Via Pydantic settings
✅ **Logging Estruturado**: Com Loguru
✅ **Testes Unitários**: Implementados e funcionando
✅ **CI/CD**: Pipeline automatizado
✅ **Documentação Completa**: README, CHANGELOG, este arquivo

## 📈 Próximos Passos

1. Adicionar mais testes unitários para dashboards
2. Implementar cache para queries pesadas
3. Criar mais componentes reutilizáveis de visualização
4. Documentar APIs dos módulos com Sphinx/MkDocs
5. Adicionar monitoramento de modelos em produção

---

**Mantido por**: Raphael Norris
**Última refatoração**: 2024-11-23
**Status**: ✅ Produção
