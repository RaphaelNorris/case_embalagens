"""
PIPELINE COMPLETO - CLUSTERIZAÇÃO + MODELAGEM + SHAP
Classificação Binária: PRODUTIVO vs IMPRODUTIVO

Autor: Raphael Norris
Data: 2025-01-16
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import GroupKFold, cross_val_score, train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve, precision_recall_curve
)
from lightgbm import LGBMClassifier
import lightgbm as lgb
import shap
import joblib
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================================================
# PARTE 1: CLUSTERIZAÇÃO (Feature Engineering)
# ============================================================================

print('='*80)
print('PARTE 1: CLUSTERIZAÇÃO - FEATURE ENGINEERING')
print('='*80)

# Carregar dados
# df_flexo_pedidos_agg já deve estar carregado no notebook
# Se não, descomente a linha abaixo:
# df_flexo_pedidos_agg = pd.read_parquet('df_flexo_pedidos_agg.parquet')

print(f'\nDataset shape: {df_flexo_pedidos_agg.shape}')
print(f'Target distribution:')
print(df_flexo_pedidos_agg['TARGET_PRODUTIVO'].value_counts())

# 1.1 Selecionar features para clustering (apenas características do produto)
features_clustering = [
    # Dimensões
    'VL_COMPRIMENTO', 'VL_LARGURA', 'VL_ALTURAINTERNA',
    'RAZAO_CHAPA_COMP_LARG', 'VOLUME_INTERNO',

    # Complexidade
    'QT_NRCORES', 'QT_VINCOS_TOTAL', 'VL_CONSUMO_COR_TOTAL',
    'VL_GRAMATURA', 'VL_AREALIQUIDAPECA',

    # Configuração
    'VL_MULTCOMP', 'VL_MULTLARG',
]

print(f'\n1.1 Features selecionadas para clustering: {len(features_clustering)}')

# Verificar NaNs
df_cluster = df_flexo_pedidos_agg[features_clustering].copy()
print(f'    NaNs encontrados: {df_cluster.isna().sum().sum()}')

# 1.2 Normalizar features (IMPORTANTE para K-Means!)
print('\n1.2 Normalizando features...')
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_cluster)

# 1.3 Elbow Method - Encontrar K ideal
print('\n1.3 Elbow Method para escolher K...')

inertias = []
silhouette_scores = []
K_range = range(2, 11)

from sklearn.metrics import silhouette_score

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))
    print(f'    K={k}: Inertia={kmeans.inertia_:.0f}, Silhouette={silhouette_scores[-1]:.3f}')

# Plotar elbow
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(K_range, inertias, marker='o', linewidth=2)
ax1.set_xlabel('Número de Clusters (K)', fontsize=12)
ax1.set_ylabel('Inércia', fontsize=12)
ax1.set_title('Elbow Method - Escolha de K', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)

ax2.plot(K_range, silhouette_scores, marker='s', linewidth=2, color='orange')
ax2.set_xlabel('Número de Clusters (K)', fontsize=12)
ax2.set_ylabel('Silhouette Score', fontsize=12)
ax2.set_title('Silhouette Score por K', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('elbow_silhouette_plot.png', dpi=300, bbox_inches='tight')
plt.show()

# 1.4 Aplicar K-Means com K escolhido
K_optimal = 5  # Ajustar baseado no gráfico
print(f'\n1.4 Aplicando K-Means com K={K_optimal}...')

kmeans = KMeans(n_clusters=K_optimal, random_state=42, n_init=10)
df_flexo_pedidos_agg['CLUSTER_PRODUTO'] = kmeans.fit_predict(X_scaled)

print(f'✓ Clustering concluído!')
print(f'  Distribuição de clusters:')
print(df_flexo_pedidos_agg['CLUSTER_PRODUTO'].value_counts().sort_index())

# 1.5 Analisar perfil dos clusters
print(f'\n1.5 PERFIL DOS CLUSTERS')
print('='*80)

cluster_profile = df_flexo_pedidos_agg.groupby('CLUSTER_PRODUTO').agg({
    'CD_OP': 'count',

    # Performance (TARGET - apenas para análise!)
    'PRODUTIVIDADE_CPM': 'mean',
    'PERC_TEMPO_PARADO': 'mean',
    'QT_PARADAS': 'mean',
    'TARGET_PRODUTIVO': 'mean',  # % produtivos

    # Características de produto
    'VL_COMPRIMENTO': 'mean',
    'VL_LARGURA': 'mean',
    'VOLUME_INTERNO': 'mean',
    'QT_NRCORES': 'mean',
    'QT_VINCOS_TOTAL': 'mean',
    'VL_GRAMATURA': 'mean',
}).round(2)

cluster_profile.columns = [
    'N_OPs', 'Produtiv', '% Parado', 'Qt Paradas', '% Produtivos',
    'Comprimento', 'Largura', 'Volume', 'Cores', 'Vincos', 'Gramatura'
]

print(cluster_profile)

# Plotar perfil dos clusters
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.ravel()

metrics = [
    ('PRODUTIVIDADE_CPM', 'Produtividade (CPM)', 'green'),
    ('PERC_TEMPO_PARADO', '% Tempo Parado', 'red'),
    ('QT_PARADAS', 'Quantidade de Paradas', 'orange'),
    ('VL_GRAMATURA', 'Gramatura (g/m²)', 'purple'),
    ('VOLUME_INTERNO', 'Volume Interno (dm³)', 'blue'),
    ('QT_NRCORES', 'Número de Cores', 'brown')
]

for i, (col, title, color) in enumerate(metrics):
    data = df_flexo_pedidos_agg.groupby('CLUSTER_PRODUTO')[col].mean()
    axes[i].bar(data.index, data.values, color=color, alpha=0.7, edgecolor='black')
    axes[i].set_xlabel('Cluster', fontsize=10)
    axes[i].set_ylabel(title, fontsize=10)
    axes[i].set_title(f'{title} por Cluster', fontsize=12, fontweight='bold')
    axes[i].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('cluster_profiles.png', dpi=300, bbox_inches='tight')
plt.show()

# Composições mais comuns por cluster
print(f'\nCOMPOSIÇÕES MAIS COMUNS POR CLUSTER:')
for cluster_id in range(K_optimal):
    print(f'\n  Cluster {cluster_id}:')
    top_comp = df_flexo_pedidos_agg[
        df_flexo_pedidos_agg['CLUSTER_PRODUTO'] == cluster_id
    ]['CAT_COMPOSICAO'].value_counts().head(5)
    for comp, count in top_comp.items():
        print(f'    {comp}: {count} OPs')

# ============================================================================
# PARTE 2: PREPARAÇÃO PARA MODELAGEM
# ============================================================================

print(f'\n{"="*80}')
print('PARTE 2: PREPARAÇÃO PARA MODELAGEM')
print('='*80)

# 2.1 Remover colunas com data leakage (MANTER CD_ITEM!)
print('\n2.1 Removendo data leakage...')

colunas_remover = [
    'CD_OP',  # Identificador
    # CD_ITEM MANTIDO! Será feature categórica

    # Target leakage
    'QT_PRODUZIDA', 'QT_CHAPASALIMENTADAS',
    'PRODUTIVIDADE_CPM', 'PRODUTIVIDADE_TOTAL_CPM',
    'EFICIENCIA_PRODUCAO_PCT', 'EFICIENCIA_TEMPO_PCT',
    'PERC_TEMPO_PARADO', 'TAXA_PARADAS_POR_HORA',
    'VL_DURACAO_PRODUCAO', 'VL_DURACAO_TOTAL',
]

df_model = df_flexo_pedidos_agg.drop(columns=colunas_remover, errors='ignore')

# Separar X e y
X = df_model.drop(columns=['TARGET_PRODUTIVO'])
y = df_model['TARGET_PRODUTIVO']

print(f'  Features (X): {X.shape}')
print(f'  Target (y): {y.shape}')
print(f'  Distribuição: {dict(y.value_counts())}')

# 2.2 Identificar features categóricas
features_cat = X.select_dtypes(include=['object', 'category']).columns.tolist()
print(f'\n2.2 Features categóricas ({len(features_cat)}):')
for feat in features_cat:
    nunique = X[feat].nunique()
    print(f'  - {feat}: {nunique} categorias')

# 2.3 Split com GroupKFold (evitar leakage entre OPs do mesmo item)
print('\n2.3 Split estratégico com GroupKFold por CD_ITEM...')

groups = df_flexo_pedidos_agg['CD_ITEM'].values

# Primeiro, fazer um split treino/teste simples
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print(f'  Treino: {len(X_train):,} ({len(X_train)/len(X)*100:.1f}%)')
print(f'  Teste: {len(X_test):,} ({len(X_test)/len(X)*100:.1f}%)')

# ============================================================================
# PARTE 3: MODELAGEM COM LIGHTGBM
# ============================================================================

print(f'\n{"="*80}')
print('PARTE 3: TREINAMENTO DO MODELO')
print('='*80)

# 3.1 Treinar modelo
print('\n3.1 Treinando LightGBM...')

model = LGBMClassifier(
    n_estimators=500,
    max_depth=7,
    learning_rate=0.05,
    num_leaves=31,
    min_child_samples=20,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=0.1,
    random_state=42,
    verbose=-1,
    n_jobs=-1
)

# Treinar
model.fit(
    X_train, y_train,
    categorical_feature=features_cat,
    eval_set=[(X_test, y_test)],
    eval_metric='auc',
    callbacks=[
        lgb.early_stopping(stopping_rounds=50, verbose=False),
        lgb.log_evaluation(period=0)
    ]
)

print(f'✓ Modelo treinado!')
print(f'  Melhor iteração: {model.best_iteration_}')

# 3.2 Predições
y_pred_proba = model.predict_proba(X_test)[:, 1]
y_pred = (y_pred_proba >= 0.5).astype(int)

# ============================================================================
# PARTE 4: AVALIAÇÃO DO MODELO
# ============================================================================

print(f'\n{"="*80}')
print('PARTE 4: AVALIAÇÃO DO MODELO')
print('='*80)

# 4.1 Métricas
print('\n4.1 Classification Report:')
print(classification_report(y_test, y_pred, target_names=['Improdutivo', 'Produtivo']))

# AUC-ROC
auc = roc_auc_score(y_test, y_pred_proba)
print(f'\nAUC-ROC: {auc:.4f}')

# 4.2 Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print(f'\nConfusion Matrix:')
print(cm)

# Visualizar
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Matriz de confusão
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Improdutivo', 'Produtivo'],
            yticklabels=['Improdutivo', 'Produtivo'],
            ax=ax1, cbar=False)
ax1.set_title('Matriz de Confusão', fontsize=14, fontweight='bold')
ax1.set_ylabel('Real', fontsize=12)
ax1.set_xlabel('Predito', fontsize=12)

# Curva ROC
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
ax2.plot(fpr, tpr, label=f'AUC = {auc:.4f}', linewidth=2)
ax2.plot([0, 1], [0, 1], 'k--', label='Random', linewidth=1)
ax2.set_xlabel('False Positive Rate', fontsize=12)
ax2.set_ylabel('True Positive Rate', fontsize=12)
ax2.set_title('Curva ROC', fontsize=14, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('model_evaluation.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================================
# PARTE 5: INTERPRETABILIDADE - SHAP
# ============================================================================

print(f'\n{"="*80}')
print('PARTE 5: INTERPRETABILIDADE (SHAP)')
print('='*80)

# 5.1 Calcular SHAP values
print('\n5.1 Calculando SHAP values (pode demorar alguns minutos)...')

explainer = shap.TreeExplainer(model)
shap_values = explainer(X_test)

print('✓ SHAP values calculados!')

# 5.2 Feature importance global
print('\n5.2 Top 20 Features Mais Importantes (Global):')

feature_importance = pd.DataFrame({
    'Feature': X_test.columns,
    'Importance': np.abs(shap_values.values).mean(axis=0)
}).sort_values('Importance', ascending=False)

print(feature_importance.head(20))

# Salvar
feature_importance.to_csv('feature_importance.csv', index=False)

# 5.3 Visualizações SHAP
print('\n5.3 Gerando visualizações SHAP...')

# Bar plot
plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_test, plot_type="bar", show=False, max_display=20)
plt.title('Top 20 Features - Importância Global', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('shap_feature_importance.png', dpi=300, bbox_inches='tight')
plt.show()

# Beeswarm plot
plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_test, show=False, max_display=20)
plt.title('Distribuição de Impactos das Features', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('shap_beeswarm.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================================
# PARTE 6: EXEMPLOS DE PREDIÇÕES INDIVIDUAIS
# ============================================================================

print(f'\n{"="*80}')
print('PARTE 6: EXEMPLOS DE PREDIÇÕES INDIVIDUAIS')
print('='*80)

# 6.1 Escolher exemplos (1 IMPRODUTIVO, 1 PRODUTIVO)
idx_improdutivo = y_test[y_test == 0].index[0]
idx_produtivo = y_test[y_test == 1].index[0]

for idx_original, label in [(idx_improdutivo, 'IMPRODUTIVO'), (idx_produtivo, 'PRODUTIVO')]:
    idx_test = X_test.index.get_loc(idx_original)

    op_exemplo = X_test.iloc[idx_test]
    shap_vals_op = shap_values[idx_test]

    # Probabilidades
    prob_improdutivo = y_pred_proba[idx_test]
    prob_produtivo = 1 - prob_improdutivo
    real = "IMPRODUTIVO" if y_test.iloc[idx_test] == 0 else "PRODUTIVO"
    pred = "IMPRODUTIVO" if y_pred[idx_test] == 0 else "PRODUTIVO"

    print(f'\n{"="*80}')
    print(f'EXEMPLO - OP {label}')
    print('='*80)
    print(f'\nÍndice: {idx_original}')
    print(f'Real: {real}')
    print(f'Predito: {pred}')
    print(f'\nProbabilidades:')
    print(f'  Improdutivo: {prob_improdutivo*100:.1f}%')
    print(f'  Produtivo: {prob_produtivo*100:.1f}%')

    # Top features que contribuíram
    feature_contrib = pd.DataFrame({
        'Feature': X_test.columns,
        'SHAP_Value': shap_vals_op.values,
        'Feature_Value': op_exemplo.values
    }).sort_values('SHAP_Value', key=abs, ascending=False)

    print(f'\nTop 10 Features que mais contribuíram:')
    for i, row in feature_contrib.head(10).iterrows():
        direction = "→ aumenta prob" if row['SHAP_Value'] > 0 else "→ diminui prob"
        print(f"  {row['Feature']:30s} = {str(row['Feature_Value'])[:10]:>10} | SHAP: {row['SHAP_Value']:>+.4f} {direction}")

    # Waterfall plot
    shap.waterfall_plot(shap_values[idx_test], show=False)
    plt.title(f'Contribuição de Features - OP {label}', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(f'shap_waterfall_op_{label}.png', dpi=300, bbox_inches='tight')
    plt.show()

# ============================================================================
# PARTE 7: SALVAMENTO DE ARTEFATOS
# ============================================================================

print(f'\n{"="*80}')
print('PARTE 7: SALVAMENTO DE ARTEFATOS')
print('='*80)

# Salvar modelos
joblib.dump(model, 'model_produtividade_lgbm.pkl')
joblib.dump(explainer, 'shap_explainer.pkl')
joblib.dump(scaler, 'scaler_clustering.pkl')
joblib.dump(kmeans, 'kmeans_model.pkl')

# Salvar dataset final
df_flexo_pedidos_agg.to_parquet('df_model_with_clusters.parquet', index=False)

# Salvar predições
resultados = pd.DataFrame({
    'Index': X_test.index,
    'Real': y_test.values,
    'Predito': y_pred,
    'Prob_Improdutivo': y_pred_proba,
    'Prob_Produtivo': 1 - y_pred_proba,
    'Cluster': df_flexo_pedidos_agg.loc[X_test.index, 'CLUSTER_PRODUTO'].values
})
resultados.to_csv('predicoes_teste.csv', index=False)

print('\n✓ Artefatos salvos:')
print('  - model_produtividade_lgbm.pkl')
print('  - shap_explainer.pkl')
print('  - scaler_clustering.pkl')
print('  - kmeans_model.pkl')
print('  - df_model_with_clusters.parquet')
print('  - predicoes_teste.csv')
print('  - feature_importance.csv')
print('  - Visualizações: PNG files')

# ============================================================================
# PARTE 8: ANÁLISE DE CLUSTERS vs PERFORMANCE
# ============================================================================

print(f'\n{"="*80}')
print('PARTE 8: ANÁLISE CLUSTERS vs PERFORMANCE')
print('='*80)

cluster_performance = resultados.groupby('Cluster').agg({
    'Index': 'count',
    'Real': 'mean',
    'Prob_Produtivo': 'mean'
}).round(3)

cluster_performance.columns = ['N_OPs_Teste', '% Real Produtivo', 'Prob Média Produtivo']
print(cluster_performance)

print(f'\n{"="*80}')
print('PIPELINE CONCLUÍDO COM SUCESSO!')
print('='*80)
print(f'\nRESUMO:')
print(f'  - Dataset: {len(df_flexo_pedidos_agg):,} OPs')
print(f'  - Features: {X.shape[1]}')
print(f'  - Clusters: {K_optimal}')
print(f'  - AUC-ROC: {auc:.4f}')
print(f'  - Treino: {len(X_train):,} / Teste: {len(X_test):,}')
print('='*80)
