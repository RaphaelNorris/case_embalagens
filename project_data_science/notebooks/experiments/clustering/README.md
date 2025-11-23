# Clustering Experiments

Experimentos de **clusterização usando Gaussian Mixture Models (GMM)** para segmentação de dados de produção.

## 📁 Conteúdo

### 40.0 - Clustering CV (GMM)
- **Arquivo**: `40.0-rn-clustering-cv-gmm-20240101.ipynb`
- **Descrição**: Clusterização GMM para máquinas tipo **CV (Cola Vertical)**
- **Algoritmo**: Gaussian Mixture Model (GMM)
- **Features**: Métricas de produção, paradas, eficiência
- **Output**: Clusters de perfis de produção CV

### 41.0 - Clustering Flexo (GMM)
- **Arquivo**: `41.0-rn-clustering-flexo-gmm-20240101.ipynb`
- **Descrição**: Clusterização GMM para máquinas tipo **Flexo (Flexografia)**
- **Algoritmo**: Gaussian Mixture Model (GMM)
- **Features**: Métricas de produção, paradas, eficiência
- **Output**: Clusters de perfis de produção Flexo

## 📊 Visualizações

### Imagens geradas pelos experimentos:

1. **`gmm_cluster_heatmap.png`**
   - Heatmap de características por cluster
   - Mostra padrões de cada segmento

2. **`gmm_clusters_pca_2d.png`**
   - Visualização 2D dos clusters via PCA
   - Separação espacial dos grupos

3. **`gmm_distribution.png`**
   - Distribuição de pontos por cluster
   - Tamanho e balanceamento dos clusters

4. **`gmm_selection_metrics.png`**
   - Métricas de seleção de K (número de clusters)
   - BIC, AIC, Silhouette Score

## 🎯 Objetivo

Identificar **perfis de produção** através de clusterização não-supervisionada:

- **Alta produtividade** com poucas paradas
- **Produtividade moderada** com paradas frequentes
- **Baixa produtividade** com problemas operacionais
- **Perfis sazonais** ou específicos de produtos

## 🔬 Metodologia

### 1. Feature Engineering
```python
# Features utilizadas
- Métricas de tempo (setup, produção, paradas)
- Eficiência e produtividade
- Contagem de paradas por tipo
- Características do produto (cliente, máquina, etc.)
```

### 2. Seleção de K (número de clusters)
```python
# Critérios
- BIC (Bayesian Information Criterion)
- AIC (Akaike Information Criterion)
- Silhouette Score
- Validação visual (PCA)
```

### 3. Interpretação
```python
# Análise por cluster
- Estatísticas descritivas
- Perfil médio
- Principais diferenciadores
```

## 📈 Resultados Esperados

**Segmentação de produção** em:
- 3-5 clusters distintos
- Clusters interpretáveis e acionáveis
- Insights para otimização

**Aplicações**:
- Predição de performance baseada em cluster
- Benchmarking entre perfis
- Identificação de anomalias (cluster "outliers")
- Recomendações customizadas por segmento

## 🔗 Relação com Outros Notebooks

**Input**: Dados preprocessados de `03-preprocessing/`
**Output**: Features de cluster para modeling em `experiments/ds-pipelines/`

## ⚙️ Configuração

### Parâmetros principais GMM:
```python
n_components = [2, 3, 4, 5, 6]  # Range de clusters a testar
covariance_type = 'full'         # Tipo de covariância
random_state = 42                # Reprodutibilidade
```

---

**Convenção de nomes**: `4X.Y-rn-clustering-tipo-YYYYMMDD.ipynb`

**Nota**: Experimentos de clustering são exploratórios. Resultados podem variar conforme dados e features selecionadas.
