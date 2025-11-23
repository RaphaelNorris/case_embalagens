# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [2.0.0] - 2024-11-23

### 🎯 Refatoração Completa

**Resumo**: Refatoração completa do repositório seguindo melhores práticas de engenharia de software para ciência de dados. Estrutura modular, documentação completa e eliminação de código duplicado.

### ✨ Adicionado

#### Estrutura Modular
- **Módulo `src/analysis/`**: Processamento e análise de dados
  - `data_processing.py`: Limpeza automática, agregações, ABC classification, detecção de outliers
- **Módulo `src/viz/`**: Visualizações reutilizáveis com Plotly
  - `plots.py`: 10+ funções de plotagem (time series, pareto, box, heatmap, 3D scatter, etc)
- **Módulo `src/dashboards/`**: Dashboards Streamlit organizados
  - `dashboard_main.py`: Dashboard multi-página principal
  - `dashboard_facas.py`: Dashboard especializado em facas/lâminas
  - `components/ui.py`: Componentes UI reutilizáveis (metric_card, insight_box, etc)

#### Configuração e Infraestrutura
- **Configuração centralizada** com Pydantic (`src/config.py`)
  - Type-safe configuration para Oracle, SQL Server, caminhos, ML
  - Validação automática de settings
- **Sistema de logging estruturado** com Loguru (`src/logger.py`)
  - Logs JSON em produção, formatados em desenvolvimento
  - Rotação automática de arquivos
- **Módulos de conexão refatorados** (`src/data/`)
  - `conn_oracle.py`: Context managers para Oracle (raw/trusted/refined)
  - `conn_sql.py`: Conexão SQL Server com múltiplos drivers
  - `data_quality.py`: Validação e monitoramento de qualidade

#### Feature Engineering e ML
- **Módulo `src/features/build_features.py`**
  - `create_temporal_features()`: Features de data/hora
  - `create_production_features()`: Rolling stats e lags
  - `create_stoppage_features()`: Análise de paradas
  - `merge_temporal_production_data()`: Merge temporal com pd.merge_asof
- **Módulo `src/models/`**: ML completo
  - `train_model.py`: Suporte para Random Forest, XGBoost, LightGBM
  - `predict_model.py`: Predições com intervalos de confiança
  - Feature importance e métricas (MAE, RMSE, R², MAPE)

#### Qualidade de Código
- **Pre-commit hooks** (`.pre-commit-config.yaml`)
  - Ruff (linting + formatting)
  - MyPy (type checking)
  - Secrets detection
  - YAML/JSON validation
- **CI/CD** (`.github/workflows/ci.yml`)
  - Testes em Python 3.10, 3.11, 3.12
  - Coverage reporting
  - Formatação e linting automático
- **Makefile** com 15+ comandos de automação
- **Testes unitários** (`tests/`)

#### Documentação Completa (3500+ linhas)
- **README por módulo** (7 arquivos):
  - `src/README.md`: Visão geral e fluxo de dados
  - `src/data/README.md`: Conexões e qualidade
  - `src/features/README.md`: Feature engineering
  - `src/models/README.md`: ML training & prediction
  - `src/viz/README.md`: Visualizações
  - `src/analysis/README.md`: Processamento de dados
  - `src/dashboards/README.md`: Dashboards Streamlit
- **README por camada de dados** (5 arquivos):
  - `data/README.md`: Medallion Architecture
  - `data/01 - raw/README.md`: Bronze layer
  - `data/02 - trusted/README.md`: Silver layer
  - `data/03 - ml/README.md`: Features ML
  - `data/04 - refined/README.md`: Gold layer
- **README por categoria de notebooks** (4 arquivos):
  - `notebooks/01-eda-tables/README.md`: EDA de 9 tabelas
  - `notebooks/02-eda-cross/README.md`: Análises cruzadas
  - `notebooks/03-preprocessing/README.md`: Pipeline de limpeza
  - `notebooks/04-production/README.md`: Notebooks de produção
- **Documentação raiz**:
  - `README.md`: Atualizado com nova estrutura
  - `PROJECT_STRUCTURE.md`: Estrutura completa do projeto
  - `CHANGELOG.md`: Este arquivo

### 🔄 Modificado

#### Notebooks (17 renomeados, 2 duplicados removidos)
- **Convenção de nomenclatura padronizada**: `##.#-author-description-YYYYMMDD.ipynb`
- **Reorganização em categorias lógicas**:
  - `notebooks/01-eda-tables/`: 9 notebooks (clientes, pedidos, itens, máquinas, facas, paradas, tarefcon)
  - `notebooks/02-eda-cross/`: 3 notebooks (pedidos-itens, tarefcon-paradas, tarefcon-itens)
  - `notebooks/03-preprocessing/`: 2 notebooks (pipeline de limpeza)
  - `notebooks/04-production/`: 2 notebooks (overview, temporal association)
- Removidos: `05.nb_eda_itens2.ipynb`, `08.1nb_tarefcon_x_paradas_refatorado.ipynb` (duplicados)

#### Estrutura de Código
- **Dashboards modularizados**:
  - `app.py` → `dashboards/dashboard_facas.py` (527 linhas)
  - `app2.py` → `dashboards/dashboard_main.py` (1604 linhas)
  - Componentes UI extraídos para `components/ui.py`
- **Dependências atualizadas** (`pyproject.toml`):
  - Organizadas por categoria (data, ML, databases, viz)
  - Grupos adicionais (dev, docs, airflow)
  - Versões pinadas para reprodutibilidade

#### Organização Geral
- **Assets organizados**: Imagens movidas para `docs/images/`
- **Estrutura de testes**: Preparada para unit/, integration/, dashboards/
- **Scripts**: Estrutura criada para data_extraction/, analysis/, deployment/, maintenance/

### 🔐 Segurança
- Detecção de secrets com pre-commit hooks
- Credenciais via variáveis de ambiente (.env)
- Validação type-safe com Pydantic
- `.gitignore` completo (dados, credenciais, caches)

### 📊 Métricas da Refatoração
- **Documentação**: +3500 linhas de READMEs
- **Modularização**: 6 módulos principais criados
- **Notebooks**: 17 renomeados, 4 categorias organizadas
- **Commits**: 4 commits principais de refatoração
  - `d00e25b`: Refatoração inicial (config, conexões, features, models)
  - `99f7b8b`: Reorganização completa (estrutura modular e notebooks)
  - `3a10dd4`: Documentação de notebooks e camadas de dados
  - `668b0d7`: Documentação completa dos módulos src/

## [0.1.0] - 2024-01-XX

### Adicionado
- Estrutura inicial do projeto
- Notebooks de análise exploratória
- Pipeline de dados com Airflow
- Dashboard Streamlit para análise de facas
- Arquitetura medallion (Bronze, Silver, Gold)

---

## Tipos de Mudanças

- `Adicionado` para novas funcionalidades
- `Modificado` para mudanças em funcionalidades existentes
- `Descontinuado` para funcionalidades que serão removidas
- `Removido` para funcionalidades removidas
- `Corrigido` para correção de bugs
- `Segurança` para vulnerabilidades corrigidas
