# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Adicionado
- Configuração centralizada com Pydantic (`src/config.py`)
- Sistema de logging estruturado com Loguru (`src/logger.py`)
- Módulos de conexão refatorados para Oracle e SQL Server
  - Context managers para gerenciamento seguro de conexões
  - Tratamento de erros aprimorado
  - Suporte a múltiplos drivers
- Módulo de feature engineering (`src/features/build_features.py`)
  - Features temporais
  - Features de produção com rolling windows e lags
  - Features de paradas de máquinas
  - Features específicas para facas/lâminas
  - Merge temporal de dados de produção
- Módulos de ML (`src/models/`)
  - Treinamento de modelos (Random Forest, XGBoost, LightGBM)
  - Avaliação de modelos
  - Predição com intervalos de confiança
  - Salvamento e carregamento de modelos
- Testes unitários completos
  - Testes de configuração
  - Testes de feature engineering
  - Testes de modelos
- Arquivos de configuração de projeto
  - `.pre-commit-config.yaml` com hooks de qualidade de código
  - `Makefile` com comandos de automação
  - `.env.example` com template de variáveis de ambiente
  - `.gitignore` completo e organizado
- CI/CD com GitHub Actions
  - Pipeline de testes automáticos
  - Linting e formatação
  - Type checking
  - Coverage reporting
- Documentação completa
  - README.md atualizado e detalhado
  - Exemplos de uso
  - Guia de contribuição

### Modificado
- `pyproject.toml` atualizado com todas as dependências necessárias
  - Dependências principais organizadas por categoria
  - Grupos de dependências (dev, docs, airflow)
  - Configuração de ferramentas de teste
- Módulos de conexão de banco de dados refatorados
  - Removidas credenciais hardcoded
  - Implementado padrão de configuração via ambiente
  - Adicionado logging apropriado

### Segurança
- Implementada detecção de secrets com pre-commit hooks
- Credenciais movidas para variáveis de ambiente
- Validação de configuração com Pydantic

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
