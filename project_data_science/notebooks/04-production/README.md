# 🚀 Produção - Notebooks de Deploy

Esta pasta contém notebooks **prontos para produção** e implementações finais de análises críticas.

## 📁 Estrutura

| Notebook | Status | Descrição |
|----------|--------|-----------|
| `00.0-rn-overview-pilot-20240101.ipynb` | Piloto | Visão geral e testes iniciais |
| `30.0-rn-production-temporal-association-20240101.ipynb` | Produção | Associação temporal de paradas com OPs |

## 🎯 Objetivo

Implementar análises **validadas e testadas** que podem ser:

1. **Executadas em Schedule** (jobs automatizados)
2. **Integradas em Pipelines** (Airflow, etc.)
3. **Deployadas como APIs** (FastAPI, Flask)
4. **Usadas em Dashboards** (Streamlit, PowerBI)

## 🔑 Notebooks de Produção

### 00.0 - Overview Pilot

**Status**: 🟡 Piloto / Prova de Conceito

**Objetivo**: Validação inicial de conceitos e fluxos

**Conteúdo**:
- Testes de conectividade
- Validação de pipelines
- Análises exploratórias de alto nível

**Próximos Passos**:
- Transformar em módulos reutilizáveis
- Adicionar testes automatizados
- Documentar APIs

### 30.0 - Associação Temporal de Paradas com OPs

**Status**: ✅ Produção

**Objetivo**: Associar paradas de máquinas com Ordens de Produção (OP) usando janelas temporais

**Problema Resolvido**:
- Paradas de máquinas não têm relação direta com OPs
- Necessário inferir qual OP estava rodando quando ocorreu a parada
- Dados de CD_OP em TarefCon não são estruturados

**Solução Implementada**:
1. **Parse de CD_OP**: Extrai ID_PEDIDO e ID_ITEM do formato "PEDIDO/ITEM"
2. **Janela Temporal**: Associa paradas com tarefas usando timestamps
3. **Inferência de Cliente**: Propaga ID_IDCLIENTE a partir de associações conhecidas

**Algoritmo**:
```python
# 1. Corrigir relações em TarefCon
df_tarefcon = corrigir_tarefcon_relacoes(df_tarefcon)

# 2. Merge temporal com paradas
merged = pd.merge_asof(
    df_tarefcon.sort_values('inicio'),
    df_paradas.sort_values('inicio'),
    on='inicio',
    by='cod_maquina',
    tolerance=pd.Timedelta(minutes=30),
    direction='nearest'
)

# 3. Análise de impacto
impact_analysis(merged)
```

**Output**:
- DataFrame com paradas associadas a OPs
- Métricas de tempo de parada por cliente/pedido/item
- Análise de causas de paradas por tipo de produto

**Uso em Produção**:
```python
from notebooks.production import temporal_association

# Carregar dados
df_tarefcon = load_trusted_data('tb_tarefcon')
df_paradas = load_trusted_data('tb_paradas')

# Associar
result = temporal_association.associate_stoppages(
    df_tarefcon,
    df_paradas,
    tolerance_minutes=30
)

# Salvar na camada Refined
save_refined_data(result, 'paradas_associadas')
```

## 🔄 Critérios para Produção

Para um notebook ser considerado "Produção", deve ter:

### ✅ Qualidade de Código
- [ ] Código modularizado (funções reutilizáveis)
- [ ] Docstrings completas
- [ ] Type hints
- [ ] Tratamento de erros
- [ ] Logging estruturado

### ✅ Testes
- [ ] Testes unitários implementados
- [ ] Casos de borda cobertos
- [ ] Validação de dados de entrada
- [ ] Assertions de qualidade

### ✅ Performance
- [ ] Otimizado para grandes volumes
- [ ] Uso eficiente de memória
- [ ] Paralelização quando aplicável
- [ ] Cache de resultados intermediários

### ✅ Documentação
- [ ] README atualizado
- [ ] Exemplos de uso
- [ ] Documentação de parâmetros
- [ ] Casos de uso descritos

### ✅ Reprodutibilidade
- [ ] Seeds fixadas (random_state)
- [ ] Dependências documentadas
- [ ] Dados de teste incluídos
- [ ] Versão de código documentada

## 🛠️ Transformação em Módulos

Código de notebooks de produção é refatorado em:

### `src/data/data_treatment.py`
```python
def corrigir_tarefcon_relacoes(df_tarefcon):
    """Corrige e infere relacionamentos em TarefCon."""
    # Código do notebook 30.0
```

### `src/features/build_features.py`
```python
def merge_temporal_production_data(df_tarefcon, df_paradas, tolerance_minutes=30):
    """Merge temporal de dados de produção."""
    # Código do notebook 30.0
```

### `src/analysis/` (futura)
```python
def analyze_stoppage_impact(df_merged):
    """Analisa impacto de paradas na produção."""
    # Análises do notebook 30.0
```

## 📊 Pipeline de Produção

```
┌──────────────────┐
│  1. Data Source  │
│  (Oracle/MSSQL)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  2. Extraction   │
│  (Airflow DAGs)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  3. Processing   │
│  (This Notebook) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  4. Storage      │
│  (Refined Layer) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  5. Consumption  │
│ (Dashboards/API) │
└──────────────────┘
```

## 🔍 Como Usar

### Desenvolvimento

```bash
cd project_data_science/notebooks/04-production
jupyter lab
```

### Produção (Scheduled)

```bash
# Via papermill (parameterização)
papermill 30.0-rn-production-temporal-association-20240101.ipynb \
    output.ipynb \
    -p start_date "2024-01-01" \
    -p end_date "2024-12-31"
```

### API (FastAPI)

```python
from fastapi import FastAPI
from src.features.build_features import merge_temporal_production_data

app = FastAPI()

@app.post("/api/associate-stoppages")
async def associate_stoppages(start_date: str, end_date: str):
    # Carrega dados
    df_tarefcon = load_data('tarefcon', start_date, end_date)
    df_paradas = load_data('paradas', start_date, end_date)

    # Processa
    result = merge_temporal_production_data(df_tarefcon, df_paradas)

    return result.to_dict(orient='records')
```

## 📈 Monitoramento

Notebooks de produção devem ter:

1. **Logging**: Registro de execução e erros
2. **Métricas**: Tempo de execução, volume processado
3. **Alertas**: Notificações em caso de falha
4. **Versionamento**: Rastreabilidade de mudanças

## 🔗 Integração com Airflow

```python
# dags/production/temporal_association_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator

def run_temporal_association():
    from src.features.build_features import merge_temporal_production_data
    # Implementação

dag = DAG('temporal_association', schedule='@daily')

task = PythonOperator(
    task_id='associate_stoppages',
    python_callable=run_temporal_association,
    dag=dag
)
```

## 📚 Veja Também

- **01-eda-tables/**: Exploração dos dados
- **02-eda-cross/**: Análises que geraram insights
- **03-preprocessing/**: Limpeza aplicada
- **src/**: Código modularizado
- **tests/**: Testes automatizados
