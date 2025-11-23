# DS Pipelines - Experimentos de Machine Learning

Notebooks experimentais de **pipelines completos** de Machine Learning para predição de produtividade e regressão de tempo.

## 📁 Estrutura

### 🔹 Pipelines de ML Completos

#### CV (Cola Vertical)
- **`pipeline_cv_ml.ipynb`** - Pipeline completo ML para CV
- **`pipeline_cv_regressor_m3h.ipynb`** - Regressor de m³/h para CV

#### Flexo (Flexografia)
- **`pipeline_flexo_ml.ipynb`** - Pipeline completo ML para Flexo
- **`pipeline_flexo_regressor_m3h.ipynb`** - Regressor de m³/h para Flexo
- **`50.0-rn-pipeline-flexo-20240101.ipynb`** - Pipeline Flexo (versão organizada)

#### Operações e Paradas
- **`51.0-rn-pipeline-ops-paradas-20240101.ipynb`** - Pipeline de análise de paradas

### 🔹 Pipelines de Regressão

- **`regressor_training_inference.ipynb`** - Training/Inference v1
- **`regressor_training_inference_corrected.ipynb`** - Training/Inference v2 (corrigido)
- **`regressor_training_inference_fixed.ipynb`** - Training/Inference v3 (fixed)

### 🔹 Notebook Principal

- **`nb_main.ipynb`** - Notebook principal de orquestração

## 🎯 Objetivo

Desenvolver e experimentar **pipelines end-to-end** de ML:

1. **Data Loading** - Carregar dados preprocessados
2. **Feature Engineering** - Criar features relevantes
3. **Feature Selection** - Selecionar features mais importantes
4. **Model Training** - Treinar modelos (CatBoost, XGBoost, RF)
5. **Model Evaluation** - Avaliar performance
6. **Hyperparameter Tuning** - Otimizar hiperparâmetros
7. **Model Persistence** - Salvar modelos treinados
8. **Inference** - Fazer predições

## 📊 Tipos de Modelos

### Classificação
- **Produtividade Alta/Baixa**
- Features: métricas de produção, paradas, setup
- Modelos: CatBoost, XGBoost, Random Forest

### Regressão
- **Predição de m³/h** (produtividade contínua)
- **Predição de tempo de produção**
- Features: características do pedido, máquina, produto
- Modelos: CatBoost Regressor, XGBoost Regressor

## 🔬 Estrutura dos Pipelines

```python
# Estrutura típica de um pipeline

1. Imports e Config
   - Bibliotecas
   - Paths (via config_manager)
   - Parâmetros

2. Data Loading
   - Carregar dados de 03-ml/ ou 04-refined/
   - Split train/test

3. Feature Engineering
   - Criar features temporais
   - Agregações
   - Ratios e métricas derivadas

4. Feature Selection
   - Mutual Information
   - Feature Importance
   - Correlation Analysis

5. Model Training
   - Treinar múltiplos modelos
   - Cross-validation
   - Hyperparameter tuning

6. Evaluation
   - Métricas (MAE, RMSE, R², etc.)
   - Visualizações
   - SHAP analysis

7. Model Persistence
   - Salvar modelo
   - Salvar preprocessors
   - Salvar metadata
```

## 📈 Métricas de Avaliação

### Regressão
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **R²** (Coefficient of Determination)
- **MAPE** (Mean Absolute Percentage Error)

### Classificação
- **Accuracy**
- **Precision / Recall / F1**
- **ROC-AUC**
- **Confusion Matrix**

## 🔗 Relação com Código de Produção

Estes **notebooks experimentais** servem de base para:

- **`src/pipelines/training/`** - Código de treinamento productizado
- **`src/pipelines/inference/`** - Código de inferência productizado
- **`src/pipelines/feature/`** - Feature engineering productizado

**Workflow**:
1. Experimentar aqui (notebooks)
2. Validar resultados
3. Refatorar para código Python em `src/`
4. Testar e versionar

## 🚀 Como Usar

### 1. Executar pipeline completo
```bash
jupyter notebook pipeline_cv_ml.ipynb
# ou
jupyter notebook pipeline_flexo_ml.ipynb
```

### 2. Treinar regressor
```bash
jupyter notebook regressor_training_inference_fixed.ipynb
```

### 3. Fazer inferência
```python
# Carregar modelo treinado
from src.ml_artifacts.model_persistence import load_model

model = load_model('cv_model_v1')
predictions = model.predict(X_new)
```

## 📝 Notas

- **Versões múltiplas**: Alguns pipelines têm v1, v2, v3 (evolutivo)
- **CV vs Flexo**: Pipelines separados por tipo de máquina
- **Experimentos**: Resultados podem variar, documentar bem
- **Reprodutibilidade**: Usar `random_state=42` sempre

## ⚠️ Diferenças CV vs Flexo

### CV (Cola Vertical)
- Setup mais rápido
- Menos paradas por troca de faca
- Produtividade mais estável

### Flexo (Flexografia)
- Setup mais complexo
- Mais paradas técnicas
- Maior variabilidade de produtos

**Implicação**: Features e modelos podem diferir entre os tipos

---

**Convenção de nomes**:
- Legacy: `pipeline_[tipo]_[task].ipynb`
- Nova: `5X.Y-rn-pipeline-[contexto]-YYYYMMDD.ipynb`

**Status**: 🧪 Experimentos ativos - resultados em validação
