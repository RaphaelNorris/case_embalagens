# 🤖 ML Layer

## Propósito
**Features engineeradas** prontas para modelos de ML.

## Features Incluídas
- Temporais (year, month, day_of_week, is_weekend)
- Agregações (rolling means, stds)
- Lags (1, 7, 30 days)
- Derivadas (durações, categorias, flags)

## Datasets
- `production_features.parquet`: Features de produção
- `pedidos_itens_diff.parquet`: Diferenças pedidos vs catálogo
- `train/test/val splits`: Divisões para ML

## Exemplo
```python
from src.features.build_features import create_temporal_features, create_production_features

df = pd.read_parquet('../02 - trusted/parquet/tb_tarefcon.parquet')
df = create_temporal_features(df, 'dt_inicio')
df = create_production_features(df, group_cols=['cod_maquina'])
df.to_parquet('production_features.parquet')
```
