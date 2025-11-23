# 🔌 Data Module

## Propósito
Gerenciamento de **conexões com bancos de dados** e **qualidade de dados**.

## Módulos

### 📊 `conn_oracle.py`
Conexões com Oracle Database (camadas Bronze/Silver/Gold).

**Funções principais:**
```python
from src.data.conn_oracle import oracle_connection

# Context manager para conexão segura
with oracle_connection('trusted') as conn:
    df = pd.read_sql("SELECT * FROM tb_clientes", conn)
```

**Camadas disponíveis:**
- `'raw'` → Dados brutos (Bronze)
- `'trusted'` → Dados limpos (Silver)
- `'refined'` → Dados agregados (Gold)

**Configuração:**
```bash
# .env
ORACLE_RAW_USER=user
ORACLE_RAW_PASSWORD=pass
ORACLE_RAW_DSN=host:1521/service

ORACLE_TRUSTED_USER=user
ORACLE_TRUSTED_PASSWORD=pass
ORACLE_TRUSTED_DSN=host:1521/service

ORACLE_REFINED_USER=user
ORACLE_REFINED_PASSWORD=pass
ORACLE_REFINED_DSN=host:1521/service
```

---

### 🗄️ `conn_sql.py`
Conexões com SQL Server (analytics).

**Funções principais:**
```python
from src.data.conn_sql import get_connection_sqlserver, safe_query_execution

# Obter conexão (tenta pymssql, depois pyodbc)
conn, method = get_connection_sqlserver()

# Executar query com segurança
df = safe_query_execution(conn, "SELECT * FROM vendas")

# Calcular diferenças entre tabelas
diff = calcular_diferencas_pedidos_itens(conn)
```

**Drivers suportados:**
1. `pymssql` (prioridade)
2. `pyodbc` com ODBC Driver 18 for SQL Server
3. `pyodbc` com ODBC Driver 17 for SQL Server
4. `pyodbc` com SQL Server Native Client 11.0

**Configuração:**
```bash
# .env
SQLSERVER_SERVER=hostname
SQLSERVER_DATABASE=db_analytics
SQLSERVER_USERNAME=user
SQLSERVER_PASSWORD=pass
```

---

### ✅ `data_quality.py`
Validação e monitoramento de qualidade dos dados.

**Funções principais:**
```python
from src.data.data_quality import check_data_quality, validate_schema

# Verificar qualidade
report = check_data_quality(df)
print(f"Missing values: {report['missing_pct']}%")
print(f"Duplicates: {report['duplicates']}")

# Validar schema
is_valid = validate_schema(df, expected_columns=['id', 'name', 'date'])
```

**Checks incluídos:**
- ❌ Missing values (por coluna)
- 🔄 Duplicados (por chave primária)
- 📊 Distribuições (outliers, skewness)
- 🔗 Integridade referencial (foreign keys)
- 📅 Datas (valores futuros, intervalos inválidos)
- 🔢 Tipos de dados (inconsistências)

---

## Exemplo Completo

```python
from src.data.conn_oracle import oracle_connection
from src.data.data_quality import check_data_quality
from src.logger import logger

# 1. Extrair dados do Oracle (camada trusted)
with oracle_connection('trusted') as conn:
    df = pd.read_sql(\"\"\"
        SELECT * FROM tb_clientes
        WHERE dt_cadastro >= TRUNC(SYSDATE) - 30
    \"\"\", conn)
    logger.info(f"Extraídos {len(df)} registros")

# 2. Validar qualidade
quality_report = check_data_quality(df)
if quality_report['missing_pct'] > 5:
    logger.warning(f"Alto percentual de missing: {quality_report['missing_pct']}%")

# 3. Processar e salvar
df.to_parquet('data/02 - trusted/tb_clientes.parquet')
```

---

## Boas Práticas

### 🔒 Segurança
- ✅ Usar variáveis de ambiente (`.env`)
- ✅ Nunca commitar credenciais
- ✅ Context managers para fechar conexões
- ✅ Tratamento de exceções específicas

### ⚡ Performance
- ✅ Usar `chunksize` para grandes volumes
- ✅ Filtrar no banco (WHERE) antes de trazer
- ✅ Criar índices em colunas de join
- ✅ Usar `read_sql_query` ao invés de `read_sql_table`

### 📊 Monitoramento
- ✅ Logar tempo de execução
- ✅ Contar registros extraídos/processados
- ✅ Alertar sobre quedas de qualidade
- ✅ Versionar schemas

---

## Troubleshooting

### Erro: `DPY-6005: cannot connect to database`
**Solução:** Verificar DSN, usuário, senha e conectividade de rede.

### Erro: `pymssql not found`
**Solução:** Instalar driver: `pip install pymssql`

### Erro: `Data source name not found`
**Solução:** Instalar ODBC Driver for SQL Server.

### Performance lenta
**Solução:**
- Adicionar índices no banco
- Usar `chunksize` para processar em lotes
- Filtrar dados no SQL (não no pandas)
