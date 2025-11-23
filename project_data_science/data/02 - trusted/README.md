# 🥈 Trusted Layer (Silver)

## Propósito
Dados **limpos, validados e padronizados**.

## Transformações
- ✅ Duplicados removidos
- ✅ Missing values tratados
- ✅ Tipos de dados corretos
- ✅ Strings padronizadas
- ✅ Relações validadas

## Tabelas Principais
- `tb_clientes.parquet`: Clientes
- `tb_pedidos.parquet`: Pedidos
- `tb_itens.parquet`: Catálogo de produtos
- `tb_maquinas.parquet`: Máquinas de produção
- `tb_facas.parquet`: Facas/lâminas
- `tb_paradas.parquet`: Paradas de máquinas
- `tb_tarefcon.parquet`: Tarefas de produção

## Exemplo
```python
from src.analysis.data_processing import clean_numeric_and_categorical

df_raw = pd.read_parquet('../01 - raw/tb_clientes.parquet')
df_clean, num_cols, cat_cols = clean_numeric_and_categorical(df_raw)
df_clean.to_parquet('tb_clientes.parquet')
```
