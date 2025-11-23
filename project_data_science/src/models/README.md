# 🤖 Models Module

## Propósito
Treinamento, avaliação e predição de **modelos de Machine Learning**.

## Módulos

### 🎓 `train_model.py`
Treina e avalia modelos de ML para previsão de produção.

### 🔮 `predict_model.py`
Realiza predições com modelos treinados.

---

## Treinamento de Modelos

### `train_production_model(X, y, model_type='random_forest', test_size=0.2, **model_params)`

Treina modelo de produção com validação automática.

**Modelos disponíveis:**
- `'random_forest'` → RandomForestRegressor (padrão)
- `'xgboost'` → XGBRegressor
- `'lightgbm'` → LGBMRegressor

**Retorno:**
- `model`: Modelo treinado
- `metrics`: Dict com métricas (MAE, RMSE, R², MAPE)

**Exemplo:**
```python
from src.models.train_model import train_production_model
import pandas as pd

# 1. Carregar features
df = pd.read_parquet('data/03 - ml/production_features.parquet')

# 2. Preparar X e y
feature_cols = [
    'quantidade_lag_1', 'quantidade_lag_7',
    'quantidade_rolling_7d_mean', 'quantidade_rolling_7d_std',
    'year', 'month', 'day_of_week'
]
X = df[feature_cols]
y = df['quantidade']

# 3. Treinar Random Forest
model, metrics = train_production_model(
    X, y,
    model_type='random_forest',
    n_estimators=100,
    max_depth=10,
    random_state=42
)

print(f"✅ MAE: {metrics['mae']:.2f}")
print(f"✅ RMSE: {metrics['rmse']:.2f}")
print(f"✅ R²: {metrics['r2']:.2f}")
```

**Parâmetros por modelo:**

**Random Forest:**
```python
model, metrics = train_production_model(
    X, y,
    model_type='random_forest',
    n_estimators=100,      # Número de árvores
    max_depth=10,          # Profundidade máxima
    min_samples_split=5,   # Mínimo para split
    random_state=42
)
```

**XGBoost:**
```python
model, metrics = train_production_model(
    X, y,
    model_type='xgboost',
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
```

**LightGBM:**
```python
model, metrics = train_production_model(
    X, y,
    model_type='lightgbm',
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    num_leaves=31,
    random_state=42
)
```

---

### `save_model(model, model_name, metadata=None)`

Salva modelo treinado com metadados.

**Exemplo:**
```python
from src.models.train_model import save_model

metadata = {
    'model_type': 'random_forest',
    'features': feature_cols,
    'metrics': metrics,
    'trained_at': '2024-01-15',
    'data_version': 'v1.0'
}

save_model(model, 'production_model_v1', metadata)
# Salvo em: models/production_model_v1.pkl
```

---

### `load_model(model_name)`

Carrega modelo salvo.

**Exemplo:**
```python
from src.models.train_model import load_model

model = load_model('production_model_v1')
# Pronto para fazer predições
```

---

## Predições

### `predict_production(model, X)`

Realiza predições com modelo treinado.

**Exemplo:**
```python
from src.models.predict_model import predict_production
import pandas as pd

# 1. Carregar modelo
model = load_model('production_model_v1')

# 2. Preparar dados novos
df_new = pd.read_parquet('data/03 - ml/production_features_new.parquet')
X_new = df_new[feature_cols]

# 3. Predizer
predictions = predict_production(model, X_new)

# 4. Adicionar ao DataFrame
df_new['quantidade_prevista'] = predictions
df_new[['dt_inicio', 'quantidade', 'quantidade_prevista']].head()
```

---

### `predict_with_confidence(model, X, confidence=0.95)`

Predições com intervalos de confiança (apenas para ensemble models).

**Exemplo:**
```python
from src.models.predict_model import predict_with_confidence

# Retorna: (predictions, lower_bound, upper_bound)
preds, lower, upper = predict_with_confidence(model, X_new, confidence=0.95)

df_new['pred'] = preds
df_new['pred_lower'] = lower
df_new['pred_upper'] = upper

# Visualizar incerteza
import plotly.graph_objects as go

fig = go.Figure([
    go.Scatter(y=df_new['quantidade'], name='Real'),
    go.Scatter(y=df_new['pred'], name='Previsto'),
    go.Scatter(y=df_new['pred_upper'], fill='tonexty', name='IC 95%'),
    go.Scatter(y=df_new['pred_lower'], fill='tonexty')
])
fig.show()
```

---

## Pipeline Completo ML

```python
import pandas as pd
from src.features.build_features import create_temporal_features, create_production_features
from src.models.train_model import train_production_model, save_model
from src.models.predict_model import predict_production
from src.logger import logger

# ========================================
# 1. FEATURE ENGINEERING
# ========================================
logger.info("📊 Carregando dados...")
df = pd.read_parquet('data/02 - trusted/tb_tarefcon.parquet')

logger.info("🛠️ Criando features...")
df = create_temporal_features(df, 'dt_inicio')
df = create_production_features(df, group_cols=['cod_maquina'])

# Remover NaN dos lags
df = df.dropna()

logger.info(f"✅ Features prontas: {df.shape}")

# ========================================
# 2. TRAIN/TEST SPLIT
# ========================================
# Divisão temporal (últimos 20% para teste)
split_idx = int(len(df) * 0.8)
df_train = df.iloc[:split_idx]
df_test = df.iloc[split_idx:]

logger.info(f"📚 Train: {len(df_train)} | Test: {len(df_test)}")

# ========================================
# 3. PREPARAR X e y
# ========================================
feature_cols = [
    'quantidade_lag_1', 'quantidade_lag_7', 'quantidade_lag_30',
    'quantidade_rolling_7d_mean', 'quantidade_rolling_7d_std',
    'year', 'month', 'day_of_week', 'is_weekend'
]

X_train = df_train[feature_cols]
y_train = df_train['quantidade']

X_test = df_test[feature_cols]
y_test = df_test['quantidade']

# ========================================
# 4. TREINAR MODELO
# ========================================
logger.info("🎓 Treinando modelo...")
model, metrics = train_production_model(
    X_train, y_train,
    model_type='xgboost',
    n_estimators=200,
    max_depth=8,
    learning_rate=0.05,
    random_state=42
)

logger.info(f"✅ MAE: {metrics['mae']:.2f}")
logger.info(f"✅ RMSE: {metrics['rmse']:.2f}")
logger.info(f"✅ R²: {metrics['r2']:.3f}")

# ========================================
# 5. SALVAR MODELO
# ========================================
metadata = {
    'model_type': 'xgboost',
    'features': feature_cols,
    'metrics': metrics,
    'trained_at': pd.Timestamp.now().isoformat()
}
save_model(model, 'production_xgb_v1', metadata)

# ========================================
# 6. AVALIAR NO TEST SET
# ========================================
logger.info("🔮 Avaliando no test set...")
y_pred = predict_production(model, X_test)

from sklearn.metrics import mean_absolute_error, r2_score
test_mae = mean_absolute_error(y_test, y_pred)
test_r2 = r2_score(y_test, y_pred)

logger.info(f"📊 Test MAE: {test_mae:.2f}")
logger.info(f"📊 Test R²: {test_r2:.3f}")

# ========================================
# 7. SALVAR PREDIÇÕES
# ========================================
df_test['quantidade_prevista'] = y_pred
df_test.to_parquet('data/04 - refined/predicoes_teste.parquet')

logger.info("✅ Pipeline ML concluído!")
```

---

## Métricas de Avaliação

### Regressão

| Métrica | Fórmula | Interpretação |
|---------|---------|---------------|
| **MAE** | `mean(|y - ŷ|)` | Erro médio absoluto (mesma unidade de y) |
| **RMSE** | `sqrt(mean((y - ŷ)²))` | Erro médio quadrático (penaliza outliers) |
| **R²** | `1 - SS_res/SS_tot` | Percentual de variância explicada (0-1) |
| **MAPE** | `mean(|y - ŷ| / y) * 100` | Erro percentual médio |

**Exemplo de interpretação:**
```
MAE: 150   → Erro médio de 150 unidades
RMSE: 200  → Erro típico de 200 unidades (alguns erros maiores)
R²: 0.85   → Modelo explica 85% da variância
MAPE: 12%  → Erro médio de 12%
```

---

## Feature Importance

```python
import pandas as pd
import plotly.express as px

# Obter importâncias
importances = model.feature_importances_
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': importances
}).sort_values('importance', ascending=False)

# Plotar
fig = px.bar(
    feature_importance,
    x='importance',
    y='feature',
    orientation='h',
    title='Feature Importance'
)
fig.show()

# Top 5 features
print(feature_importance.head())
```

---

## Boas Práticas

### 🎯 Modelagem
- ✅ Divisão temporal (não aleatória) para time series
- ✅ Validação cruzada (k-fold ou time series split)
- ✅ Tuning de hiperparâmetros (GridSearch, Optuna)
- ✅ Ensemble de modelos (média de predições)

### 📊 Monitoramento
- ✅ Salvar métricas em cada treino
- ✅ Versionar modelos (production_v1, production_v2)
- ✅ Monitorar drift de features (distribuições)
- ✅ A/B testing de modelos em produção

### 🔍 Validação
- ✅ Analisar resíduos (y - ŷ)
- ✅ Checar overfitting (train vs test)
- ✅ Validar predições (range, NaN)
- ✅ Interpretar feature importance

---

## Troubleshooting

### Erro: `ValueError: Input contains NaN`
**Solução:** Remover NaN antes de treinar: `df.dropna()` ou `.fillna(0)`

### Erro: `ImportError: xgboost not found`
**Solução:** Instalar: `pip install xgboost lightgbm`

### Modelo com R² negativo
**Solução:** Modelo pior que baseline. Revisar features e parâmetros.

### Overfitting (train R² >> test R²)
**Solução:**
- Reduzir `max_depth`
- Aumentar `min_samples_split`
- Adicionar regularização (L1/L2)
- Coletar mais dados
