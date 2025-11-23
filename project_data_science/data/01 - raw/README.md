# 🥉 Raw Layer (Bronze)

## Propósito
Dados **brutos sem transformações**, exatamente como extraídos da fonte.

## Características
- Formato original preservado
- Sem limpeza ou validação
- Histórico completo
- Schema on read

## Fontes
- Oracle Database
- SQL Server
- Arquivos CSV/Excel

## Formato
- `.parquet` (comprimido)
- `.csv` (pequenos volumes)

## Exemplo de Uso
```python
from src.data.conn_oracle import oracle_connection

with oracle_connection('raw') as conn:
    df = pd.read_sql("SELECT * FROM tb_clientes", conn)
    df.to_parquet('01 - raw/tb_clientes.parquet')
```
