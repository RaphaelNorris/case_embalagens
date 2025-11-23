# 🧹 Pré-processamento e Limpeza de Dados

Esta pasta contém notebooks de **preparação, limpeza e transformação de dados** para análise e modelagem.

## 📁 Estrutura

| Notebook | Foco | Descrição |
|----------|------|-----------|
| `20.0-rn-preprocessing-refined-20240101.ipynb` | Camada Refined | Preparação de dados para camada analítica (Gold) |
| `20.1-rn-preprocessing-tables-20240101.ipynb` | Múltiplas Tabelas | Limpeza e padronização de todas as tabelas |

## 🎯 Objetivo

Transformar dados **brutos** (Raw/Trusted) em dados **limpos e estruturados** (Refined/ML) prontos para:

1. **Análise Analítica** (BI, dashboards)
2. **Machine Learning** (features engineeradas)
3. **Produção** (dados validados e confiáveis)

## 🔄 Pipeline de Processamento

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌───────────┐
│   🥉 Raw    │────▶│  🥈 Trusted  │────▶│  🧹 Clean   │────▶│  🥇 Gold  │
│  (Bronze)   │     │   (Silver)   │     │ (Processo)  │     │ (Refined) │
└─────────────┘     └──────────────┘     └─────────────┘     └───────────┘
  Extração           Validação            Transformação       Consumo
```

## 📊 Operações de Pré-processamento

### 1. Limpeza de Dados

**Valores Ausentes**:
- Identificação de padrões de missingness
- Imputação estratégica (média, mediana, forward-fill)
- Documentação de decisões

**Duplicados**:
- Detecção de registros duplicados
- Análise de chaves compostas
- Remoção ou marcação

**Outliers**:
- Detecção (IQR, Z-score, isolationforest)
- Análise de impacto
- Tratamento ou remoção

### 2. Transformações

**Tipos de Dados**:
- Conversão de tipos (str → numeric, str → datetime)
- Padronização de formatos
- Encoding categórico

**Normalização**:
- Strings (uppercase, trim, remove special chars)
- Números (scaling, normalization)
- Datas (timezone, formato padrão)

**Derivações**:
- Colunas calculadas
- Flags booleanas
- Categorias derivadas

### 3. Enriquecimento

**Relações**:
- Inferência de chaves faltantes
- Propagação de dados (ex: cliente → pedido)
- Joins e merges

**Features**:
- Agregações
- Estatísticas móveis
- Lags temporais

## 🛠️ Funções Implementadas

Baseado nas limpezas realizadas, foram criadas funções em:

### `src/data/data_treatment.py`
```python
corrigir_tarefcon_relacoes(df_tarefcon)
# Infere ID_PEDIDO e ID_ITEM a partir de CD_OP
# Propaga ID_IDCLIENTE
```

### `src/analysis/data_processing.py`
```python
clean_numeric_and_categorical(df, threshold=0.9)
# Classifica colunas em numéricas ou categóricas
# Preenche missing values
```

### `src/features/build_features.py`
```python
create_temporal_features(df, datetime_col)
# Extrai year, month, day, day_of_week, etc.

create_production_features(df, group_cols)
# Rolling means, lags, agregações
```

## 📋 Checklist de Qualidade

Para cada tabela processada, verificar:

- [ ] **Tipos de dados corretos**
- [ ] **Sem valores ausentes críticos**
- [ ] **Sem duplicados não intencionais**
- [ ] **Outliers tratados ou documentados**
- [ ] **Relações validadas**
- [ ] **Datas no formato correto**
- [ ] **Strings padronizadas**
- [ ] **Features derivadas criadas**

## 🔍 Como Usar

1. **Pré-requisitos**:
   - Dados na camada Trusted (02 - trusted/)
   - Insights da análise exploratória (01-eda-tables, 02-eda-cross)

2. Execute na ordem:
   ```bash
   cd project_data_science/notebooks/03-preprocessing
   jupyter lab

   # Execute primeiro:
   20.0-rn-preprocessing-refined-20240101.ipynb

   # Depois:
   20.1-rn-preprocessing-tables-20240101.ipynb
   ```

3. Dados limpos serão salvos em:
   - `data/03 - ml/`: Features para ML
   - `data/04 - refined/`: Dados analíticos

## 💡 Decisões de Pré-processamento

### Status das Facas
- **Problema**: Códigos numéricos como string ("1.0", "2.0")
- **Solução**: Conversão para int, mapeamento para labels
- **Função**: `canonical_status_code()` em dashboard_facas.py

### CD_OP em TarefCon
- **Problema**: Formato não estruturado "PEDIDO/ITEM"
- **Solução**: Parsing e inferência de ID_PEDIDO e ID_ITEM
- **Função**: `corrigir_tarefcon_relacoes()` em data_treatment.py

### Valores Numéricos
- **Problema**: Colunas numéricas como string
- **Solução**: Coerção com threshold (90% numéricos)
- **Função**: `clean_numeric_and_categorical()` em data_processing.py

## 📊 Métricas de Qualidade

Após pré-processamento, os dados devem ter:

| Métrica | Target | Justificativa |
|---------|--------|---------------|
| Missing Values | < 5% | Dados completos para análise |
| Duplicados | 0% | Integridade dos dados |
| Tipos Incorretos | 0% | Processamento sem erros |
| Outliers Extremos | < 1% | Dados representativos |

## 🔗 Próximos Passos

Após pré-processamento:
- **04-production/**: Aplicar em produção
- **Modelagem**: Treinar modelos ML
- **Dashboards**: Visualização dos dados limpos

## 📚 Referências

- [Data Cleaning Best Practices](https://github.com/sfbrigade/data-science-wg/blob/master/dswg_project_resources/Data-Cleaning-Best-Practices.md)
- [Pandas Data Cleaning](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Feature Engineering Guide](https://www.kaggle.com/learn/feature-engineering)
