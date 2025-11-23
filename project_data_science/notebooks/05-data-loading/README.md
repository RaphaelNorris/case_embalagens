# 05. Data Loading

Notebooks de **carga e atualização de dados** das camadas Bronze (raw) e Silver (trusted).

## 📁 Conteúdo

### 50.0 - Load/Update Trusted
- **Arquivo**: `50.0-rn-load-update-trusted-20240101.ipynb`
- **Descrição**: Carregamento e atualização de dados na camada Silver (trusted)
- **Fonte**: Oracle Database → Parquet
- **Output**: `data/02 - trusted/*.parquet`

### 51.0 - Load Raw (SQL)
- **Arquivo**: `51.0-rn-load-raw-sql-20240101.ipynb`
- **Descrição**: Carregamento de dados raw via SQL
- **Fonte**: SQL Server / Oracle
- **Output**: `data/01 - raw/*.parquet`

## 🔄 Fluxo de Dados

```
┌─────────────────┐
│  Oracle DB /    │
│  SQL Server     │
└────────┬────────┘
         │
         ├─────────────► 51.0 Raw Loading ──► 01 - raw/
         │
         └─────────────► 50.0 Trusted Loading ──► 02 - trusted/
```

## 🎯 Uso

### Carregar dados Trusted (Silver)
```python
# Notebook: 50.0-rn-load-update-trusted-20240101.ipynb
# Atualiza dados da camada Silver
```

### Carregar dados Raw (Bronze)
```python
# Notebook: 51.0-rn-load-raw-sql-20240101.ipynb
# Extração inicial ou refresh de dados raw
```

## 📊 Outputs

**Relatórios**:
- `relatorio_tarefcon.html` - Relatório de qualidade da tabela tarefcon

## 🔗 Próximos Passos

Após carregar os dados:
1. **EDA**: Análise exploratória → `01-eda-tables/`
2. **Preprocessing**: Limpeza e transformação → `03-preprocessing/`
3. **Modeling**: Treinamento de modelos → `experiments/`

---

**Convenção de nomes**: `5X.Y-rn-tipo-contexto-YYYYMMDD.ipynb`
