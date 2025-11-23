# 🥇 Refined Layer (Gold)

## Propósito
Dados **agregados e otimizados** para BI e dashboards.

## Características
- Denormalização
- Agregações pré-calculadas
- Métricas de negócio
- Otimizado para leitura

## Agregações Típicas
- KPIs de produção (diário, semanal, mensal)
- Métricas de paradas por máquina/cliente
- Análise ABC de clientes/produtos
- Performance de máquinas

## Exemplo
```python
# Agregação mensal
df_monthly = df.groupby(['year', 'month', 'cod_maquina']).agg({
    'quantidade': 'sum',
    'tempo_parada': 'sum'
}).reset_index()

df_monthly.to_parquet('kpis_producao_mensal.parquet')
```
