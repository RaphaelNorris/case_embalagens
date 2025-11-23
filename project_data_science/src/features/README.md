# 🛠️ Features Module

## Propósito
**Feature engineering** para modelos de Machine Learning.

## Função Principal

### `build_features.py`
Criação sistemática de features temporais, agregadas e derivadas.

---

## Funções Disponíveis

### 📅 `create_temporal_features(df, datetime_col)`
Cria features temporais a partir de uma coluna de data/hora.

**Features criadas:**
- `year`, `month`, `day`, `day_of_week`, `quarter`
- `is_weekend` (boolean)
- `is_month_start`, `is_month_end` (boolean)
- `week_of_year`, `day_of_year`

**Exemplo:**
```python
from src.features.build_features import create_temporal_features

df = pd.read_parquet('data/02 - trusted/tb_tarefcon.parquet')
df = create_temporal_features(df, 'dt_inicio')

# Novas colunas: year, month, day, is_weekend, etc.
print(df[['dt_inicio', 'year', 'month', 'is_weekend']].head())
```

---

### 📊 `create_production_features(df, group_cols, value_col='quantidade')`
Cria features agregadas de produção por grupo.

**Features criadas:**
- **Rolling means:** `quantidade_rolling_7d_mean`, `quantidade_rolling_14d_mean`, `quantidade_rolling_30d_mean`
- **Rolling stds:** `quantidade_rolling_7d_std`, `quantidade_rolling_14d_std`, `quantidade_rolling_30d_std`
- **Lags:** `quantidade_lag_1`, `quantidade_lag_7`, `quantidade_lag_30`
- **Agregações:** `count`, `mean`, `std`, `min`, `max` por grupo

**Exemplo:**
```python
from src.features.build_features import create_production_features

df = pd.read_parquet('data/02 - trusted/tb_tarefcon.parquet')
df = create_production_features(
    df,
    group_cols=['cod_maquina'],
    value_col='quantidade'
)

# Novas colunas: quantidade_rolling_7d_mean, quantidade_lag_1, etc.
df.to_parquet('data/03 - ml/production_features.parquet')
```

---

### ⏸️ `create_stoppage_features(df_paradas, df_tarefcon)`
Cria features de paradas de máquinas.

**Features criadas:**
- `duracao_parada_minutos`: Duração da parada em minutos
- `tempo_desde_ultima_parada`: Tempo desde a última parada
- `frequencia_paradas_7d`: Frequência de paradas nos últimos 7 dias
- `duracao_media_paradas_7d`: Duração média das paradas nos últimos 7 dias

**Exemplo:**
```python
from src.features.build_features import create_stoppage_features

df_paradas = pd.read_parquet('data/02 - trusted/tb_paradas.parquet')
df_tarefcon = pd.read_parquet('data/02 - trusted/tb_tarefcon.parquet')

df_features = create_stoppage_features(df_paradas, df_tarefcon)
df_features.to_parquet('data/03 - ml/stoppage_features.parquet')
```

---

### 🔪 `create_knife_blade_features(df_facas)`
Cria features de facas/lâminas.

**Features criadas:**
- `comprimento_metros`: Comprimento da lâmina em metros
- `status_encoded`: Encoding numérico do status (NOVA=0, USADA=1, REFORMA=2)
- `is_ativa`: Flag booleana se a faca está ativa

**Exemplo:**
```python
from src.features.build_features import create_knife_blade_features

df_facas = pd.read_parquet('data/02 - trusted/tb_facas.parquet')
df_features = create_knife_blade_features(df_facas)

print(df_features[['cod_faca', 'comprimento_metros', 'is_ativa']].head())
```

---

### 🔗 `merge_temporal_production_data(df_tarefcon, df_paradas, tolerance_minutes=30)`
Faz merge temporal entre tarefas e paradas usando `pd.merge_asof`.

**Lógica:**
- Associa paradas a tarefas que ocorreram próximas no tempo
- Usa `tolerance_minutes` para definir janela de associação
- Permite análise de causa-efeito entre paradas e produção

**Exemplo:**
```python
from src.features.build_features import merge_temporal_production_data

df_tarefcon = pd.read_parquet('data/02 - trusted/tb_tarefcon.parquet')
df_paradas = pd.read_parquet('data/02 - trusted/tb_paradas.parquet')

df_merged = merge_temporal_production_data(
    df_tarefcon,
    df_paradas,
    tolerance_minutes=30
)

# Agora df_merged tem informações de tarefas + paradas associadas
df_merged.to_parquet('data/03 - ml/tarefcon_paradas_merged.parquet')
```

---

## Pipeline Completo

```python
import pandas as pd
from src.features.build_features import (
    create_temporal_features,
    create_production_features,
    create_stoppage_features,
    merge_temporal_production_data
)

# 1. Carregar dados da camada trusted
df_tarefcon = pd.read_parquet('data/02 - trusted/tb_tarefcon.parquet')
df_paradas = pd.read_parquet('data/02 - trusted/tb_paradas.parquet')

# 2. Features temporais
df_tarefcon = create_temporal_features(df_tarefcon, 'dt_inicio')

# 3. Features de produção
df_tarefcon = create_production_features(
    df_tarefcon,
    group_cols=['cod_maquina'],
    value_col='quantidade'
)

# 4. Features de paradas
df_stoppage = create_stoppage_features(df_paradas, df_tarefcon)

# 5. Merge temporal
df_final = merge_temporal_production_data(df_tarefcon, df_stoppage)

# 6. Salvar na camada ML
df_final.to_parquet('data/03 - ml/production_features.parquet')
print(f"✅ Features criadas: {df_final.shape[1]} colunas, {len(df_final)} registros")
```

---

## Boas Práticas

### 🎯 Feature Engineering
- ✅ Documentar cada feature criada (significado, fórmula)
- ✅ Validar distribuições (sem NaN inesperados)
- ✅ Checar correlações antes de adicionar
- ✅ Versionar features (data/03 - ml/features_v1.parquet)

### ⚡ Performance
- ✅ Usar `pd.merge_asof` para merges temporais (mais rápido)
- ✅ Evitar loops Python (usar `.groupby()` e `.rolling()`)
- ✅ Processar em chunks para grandes volumes
- ✅ Salvar em `.parquet` (mais rápido que CSV)

### 🔍 Validação
- ✅ Checar `df.isna().sum()` após cada transformação
- ✅ Validar tipos de dados (`df.dtypes`)
- ✅ Comparar estatísticas antes/depois (`df.describe()`)
- ✅ Plotar distribuições (`sns.histplot()`)

---

## Ordem de Execução

```mermaid
graph LR
    A[Trusted Layer] --> B[Temporal Features]
    B --> C[Production Features]
    C --> D[Stoppage Features]
    D --> E[Merge Temporal]
    E --> F[ML Layer]
```

1. **Trusted Layer** → Dados limpos
2. **Temporal Features** → Extrair componentes de datas
3. **Production Features** → Rolling stats e lags
4. **Stoppage Features** → Análise de paradas
5. **Merge Temporal** → Associar eventos próximos
6. **ML Layer** → Dados prontos para treino

---

## Troubleshooting

### Erro: `KeyError: 'dt_inicio'`
**Solução:** Verificar se a coluna existe e tem o nome correto.

### Erro: `ValueError: No objects to concatenate`
**Solução:** DataFrame vazio. Verificar filtros aplicados antes.

### Warning: `NaN values after rolling`
**Solução:** Normal para primeiras linhas. Usar `df.dropna()` ou `.fillna(0)`.

### Performance lenta em `rolling()`
**Solução:**
- Reduzir janelas (ex: 7d ao invés de 30d)
- Processar por chunks
- Usar `.numba=True` (se disponível)
