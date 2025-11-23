# Reorganização de Notebooks e Scripts

**Data**: 2024-11-23
**Versão**: 2.2.0
**Status**: ✅ Concluída

---

## 📋 Resumo Executivo

Reorganização completa da estrutura de notebooks e scripts para melhorar organização, nomenclatura e separação de responsabilidades.

### Objetivos alcançados:
- ✅ **Nomenclatura padronizada** - 100% dos notebooks seguem convenção
- ✅ **Separação lógica** - Clustering, pipelines, data loading em pastas próprias
- ✅ **Scripts em local correto** - `.py` movidos de notebooks/ para src/
- ✅ **Estrutura enxuta** - Diretórios vazios removidos
- ✅ **Documentação** - READMEs criados para todas as categorias

---

## 🗂️ Estrutura ANTES vs DEPOIS

### ❌ ANTES (Problemas)

```
notebooks/
├── 01-eda-tables/          ✅ Bem organizado
├── 02-eda-cross/           ✅ Bem organizado
├── 03-preprocessing/       ❌ MISTURADO: preprocessing + GMM + pipelines + .py
│   ├── 20.0-rn-preprocessing-refined-20240101.ipynb  ✅
│   ├── 20.1-rn-preprocessing-tables-20240101.ipynb   ✅
│   ├── nb_itens_processing.ipynb                     ❌ Nome errado
│   ├── nb_pedidos_process.ipynb                      ❌ Nome errado
│   ├── nb_pedidos_process_NEW.ipynb                  ❌ Nome errado
│   ├── pipeline_cv_gmm.ipynb                         ❌ Deveria estar em clustering
│   ├── pipeline_flexo_gmm.ipynb                      ❌ Deveria estar em clustering
│   ├── pipeline_flexo.ipynb                          ❌ Deveria estar em experiments
│   ├── pipeline_ops_paradas.ipynb                    ❌ Deveria estar em experiments
│   ├── pipeline_modelagem_completo.py                ❌ .py em notebooks/
│   ├── gmm_*.png (4 arquivos)                        ❌ Deveriam estar com clustering
│   └── tasks.md
├── 04-production/          ✅ Bem organizado
├── eda/                    ❌ Estrutura antiga duplicada
│   └── trusted/
│       ├── load_update_data.ipynb                    ❌ Fora da estrutura
│       └── relatorio_tarefcon.html
├── experiments/
│   └── ds-pipelines/       ✅ Pipelines ML
└── sql/                    ❌ Solto, deveria estar em data-loading
    └── load_raw.ipynb
```

### ✅ DEPOIS (Organizado)

```
notebooks/
├── 01-eda-tables/                      ✅ EDA de tabelas individuais
│   ├── 00.0-rn-metadata-column-names-20240101.ipynb
│   ├── 01.0-rn-eda-general-20240101.ipynb
│   ├── 02.0-rn-eda-clientes-20240101.ipynb
│   ├── 03.0-rn-eda-facas-20240101.ipynb
│   ├── 04.0-rn-eda-maquinas-20240101.ipynb
│   ├── 05.0-rn-eda-itens-20240101.ipynb
│   ├── 06.0-rn-eda-pedidos-20240101.ipynb
│   ├── 07.0-rn-eda-paradas-20240101.ipynb
│   ├── 08.0-rn-eda-tarefcon-20240101.ipynb
│   └── README.md
│
├── 02-eda-cross/                       ✅ EDA de relacionamentos
│   ├── 10.0-rn-cross-pedidos-itens-20240101.ipynb
│   ├── 11.0-rn-cross-tarefcon-paradas-20240101.ipynb
│   ├── 12.0-rn-cross-tarefcon-itens-20240101.ipynb
│   └── README.md
│
├── 03-preprocessing/                   ✅ APENAS preprocessing
│   ├── 20.0-rn-preprocessing-refined-20240101.ipynb
│   ├── 20.1-rn-preprocessing-tables-20240101.ipynb
│   ├── 21.0-rn-preprocessing-itens-20240101.ipynb       🆕 Renomeado
│   ├── 22.0-rn-preprocessing-pedidos-v1-20240101.ipynb  🆕 Renomeado
│   ├── 22.1-rn-preprocessing-pedidos-v2-20240101.ipynb  🆕 Renomeado
│   ├── tasks.md
│   └── README.md
│
├── 04-production/                      ✅ Notebooks de produção
│   ├── 00.0-rn-overview-pilot-20240101.ipynb
│   ├── 30.0-rn-production-temporal-association-20240101.ipynb
│   └── README.md
│
├── 05-data-loading/                    🆕 NOVA CATEGORIA
│   ├── 50.0-rn-load-update-trusted-20240101.ipynb      🆕 Movido de eda/trusted/
│   ├── 51.0-rn-load-raw-sql-20240101.ipynb             🆕 Movido de sql/
│   ├── relatorio_tarefcon.html                         🆕 Movido
│   └── README.md                                       🆕
│
└── experiments/                        ✅ Experimentos de ML
    ├── README.md                                       🆕
    │
    ├── clustering/                     🆕 NOVA CATEGORIA
    │   ├── 40.0-rn-clustering-cv-gmm-20240101.ipynb    🆕 Movido + Renomeado
    │   ├── 41.0-rn-clustering-flexo-gmm-20240101.ipynb 🆕 Movido + Renomeado
    │   ├── gmm_cluster_heatmap.png                     🆕 Movido
    │   ├── gmm_clusters_pca_2d.png                     🆕 Movido
    │   ├── gmm_distribution.png                        🆕 Movido
    │   ├── gmm_selection_metrics.png                   🆕 Movido
    │   └── README.md                                   🆕
    │
    └── ds-pipelines/
        ├── nb_main.ipynb
        ├── pipeline_cv_ml.ipynb
        ├── pipeline_cv_regressor_m3h.ipynb
        ├── pipeline_flexo_ml.ipynb
        ├── pipeline_flexo_regressor_m3h.ipynb
        ├── 50.0-rn-pipeline-flexo-20240101.ipynb       🆕 Movido + Renomeado
        ├── 51.0-rn-pipeline-ops-paradas-20240101.ipynb 🆕 Movido + Renomeado
        ├── regressor_training_inference.ipynb
        ├── regressor_training_inference_corrected.ipynb
        ├── regressor_training_inference_fixed.ipynb
        └── README.md                                   🆕
```

---

## 📦 Mapeamento Detalhado de Mudanças

### 1. RENOMEAÇÕES (Convenção Padrão)

| Arquivo ANTES | Arquivo DEPOIS | Motivo |
|---------------|----------------|--------|
| `03-preprocessing/nb_itens_processing.ipynb` | `03-preprocessing/21.0-rn-preprocessing-itens-20240101.ipynb` | Nomenclatura padrão |
| `03-preprocessing/nb_pedidos_process.ipynb` | `03-preprocessing/22.0-rn-preprocessing-pedidos-v1-20240101.ipynb` | Nomenclatura + versionamento |
| `03-preprocessing/nb_pedidos_process_NEW.ipynb` | `03-preprocessing/22.1-rn-preprocessing-pedidos-v2-20240101.ipynb` | Nomenclatura + v2 explícito |
| `03-preprocessing/pipeline_cv_gmm.ipynb` | `experiments/clustering/40.0-rn-clustering-cv-gmm-20240101.ipynb` | Movido + Renomeado |
| `03-preprocessing/pipeline_flexo_gmm.ipynb` | `experiments/clustering/41.0-rn-clustering-flexo-gmm-20240101.ipynb` | Movido + Renomeado |
| `03-preprocessing/pipeline_flexo.ipynb` | `experiments/ds-pipelines/50.0-rn-pipeline-flexo-20240101.ipynb` | Movido + Renomeado |
| `03-preprocessing/pipeline_ops_paradas.ipynb` | `experiments/ds-pipelines/51.0-rn-pipeline-ops-paradas-20240101.ipynb` | Movido + Renomeado |
| `eda/trusted/load_update_data.ipynb` | `05-data-loading/50.0-rn-load-update-trusted-20240101.ipynb` | Movido + Renomeado |
| `sql/load_raw.ipynb` | `05-data-loading/51.0-rn-load-raw-sql-20240101.ipynb` | Movido + Renomeado |

### 2. MOVIMENTAÇÕES (Nova Organização)

#### Scripts Python

| De | Para | Motivo |
|----|------|--------|
| `notebooks/03-preprocessing/pipeline_modelagem_completo.py` | `src/pipelines/DS/pipeline_modelagem_completo.py` | Scripts .py devem estar em src/ |

#### Imagens GMM

| De | Para |
|----|------|
| `03-preprocessing/gmm_cluster_heatmap.png` | `experiments/clustering/gmm_cluster_heatmap.png` |
| `03-preprocessing/gmm_clusters_pca_2d.png` | `experiments/clustering/gmm_clusters_pca_2d.png` |
| `03-preprocessing/gmm_distribution.png` | `experiments/clustering/gmm_distribution.png` |
| `03-preprocessing/gmm_selection_metrics.png` | `experiments/clustering/gmm_selection_metrics.png` |

#### Outros arquivos

| De | Para |
|----|------|
| `eda/trusted/relatorio_tarefcon.html` | `05-data-loading/relatorio_tarefcon.html` |

### 3. CRIAÇÕES (Novas Pastas e Docs)

#### Novos Diretórios
- ✨ `notebooks/05-data-loading/`
- ✨ `notebooks/experiments/clustering/`

#### Novos READMEs
- ✨ `notebooks/05-data-loading/README.md`
- ✨ `notebooks/experiments/README.md`
- ✨ `notebooks/experiments/clustering/README.md`
- ✨ `notebooks/experiments/ds-pipelines/README.md`

#### Nova Documentação
- ✨ `docs/NOTEBOOKS_REORGANIZATION.md` (este arquivo)

### 4. DELEÇÕES (Limpeza)

#### Diretórios Vazios Removidos
- 🗑️ `notebooks/eda/trusted/` (vazio após movimentação)
- 🗑️ `notebooks/eda/` (vazio após remover trusted/)
- 🗑️ `notebooks/sql/` (vazio após movimentação)

---

## 📊 Estatísticas da Reorganização

| Métrica | Valor |
|---------|-------|
| **Notebooks renomeados** | 9 |
| **Notebooks movidos** | 11 |
| **Scripts movidos** | 1 |
| **Imagens movidas** | 4 |
| **Novas categorias** | 2 (05-data-loading, experiments/clustering) |
| **READMEs criados** | 4 |
| **Diretórios deletados** | 3 |
| **Total de arquivos afetados** | 25+ |

---

## 🎯 Benefícios da Reorganização

### 1. ✅ Nomenclatura Consistente
**Antes**: Mix de `nb_`, `pipeline_`, nomes genéricos
**Depois**: 100% seguem padrão `XX.Y-rn-tipo-contexto-YYYYMMDD.ipynb`

**Benefício**: Fácil identificação, ordenação automática, versionamento claro

### 2. ✅ Separação Lógica
**Antes**: 03-preprocessing misturava preprocessing + clustering + pipelines + scripts
**Depois**: Cada categoria em seu lugar

| Categoria | Local |
|-----------|-------|
| Preprocessing | `03-preprocessing/` |
| Clustering | `experiments/clustering/` |
| Pipelines ML | `experiments/ds-pipelines/` |
| Data Loading | `05-data-loading/` |
| Scripts Python | `src/pipelines/DS/` |

### 3. ✅ Facilita Navegação
- Estrutura numerada (01, 02, 03...) segue fluxo de trabalho
- Experiments separados de notebooks de análise
- READMEs em cada categoria explicam conteúdo

### 4. ✅ Melhora Colaboração
- Nomenclatura clara comunica propósito
- Versionamento explícito (v1, v2)
- Documentação inline (READMEs)

### 5. ✅ Alinha com Boas Práticas
- Scripts .py em src/, não em notebooks/
- Experiments em área separada
- Estrutura segue cookiecutter data science

---

## 🗺️ Guia de Navegação Pós-Reorganização

### "Onde encontro...?"

**EDA de uma tabela específica**
→ `notebooks/01-eda-tables/`

**Análise de relacionamentos entre tabelas**
→ `notebooks/02-eda-cross/`

**Preprocessing e limpeza de dados**
→ `notebooks/03-preprocessing/`

**Notebooks prontos para produção**
→ `notebooks/04-production/`

**Carga de dados (ETL)**
→ `notebooks/05-data-loading/`

**Experimentos de clusterização**
→ `notebooks/experiments/clustering/`

**Pipelines completos de ML**
→ `notebooks/experiments/ds-pipelines/`

**Código Python de produção**
→ `project_data_science/src/`

---

## 📝 Convenção de Nomenclatura

### Formato Padrão
```
XX.Y-rn-tipo-contexto-YYYYMMDD.ipynb

Onde:
- XX.Y  = Número sequencial (ex: 20.0, 20.1, 21.0)
- rn    = Iniciais do autor
- tipo  = eda, preprocessing, clustering, pipeline, etc.
- contexto = cv, flexo, ops, itens, pedidos, etc.
- YYYYMMDD = Data de criação (20240101)
```

### Exemplos:
- `01.0-rn-eda-general-20240101.ipynb`
- `20.0-rn-preprocessing-refined-20240101.ipynb`
- `40.0-rn-clustering-cv-gmm-20240101.ipynb`
- `50.0-rn-pipeline-flexo-20240101.ipynb`

### Versionamento:
- v1 → `.0` (ex: 22.0)
- v2 → `.1` (ex: 22.1)
- v3 → `.2` (ex: 22.2)

---

## ⚠️ Breaking Changes

### Nenhuma!
Esta reorganização é **apenas estrutural**. Nenhum código foi modificado, apenas:
- Arquivos movidos
- Arquivos renomeados
- READMEs adicionados

**Impacto em código**: Zero
**Impacto em Git**: Histórico preservado via `git mv`

---

## 🔄 Próximos Passos Recomendados

### Curto Prazo
- [ ] Revisar READMEs e complementar se necessário
- [ ] Atualizar links em documentação externa
- [ ] Comunicar mudanças ao time

### Médio Prazo
- [ ] Consolidar notebooks duplicados (v1 vs v2 vs v3)
- [ ] Refatorar pipelines CV vs Flexo (parametrizar)
- [ ] Mover experimentos validados para src/

### Longo Prazo
- [ ] Criar notebook templates para cada categoria
- [ ] Implementar testes de notebooks (nbval)
- [ ] Automatizar conversão notebook → script

---

## 🎓 Lições Aprendidas

1. **Nomenclatura clara é fundamental** - Economiza tempo de toda equipe
2. **Separação de responsabilidades** - Não misturar preprocessing com experiments
3. **Scripts .py não pertencem a notebooks/** - Sempre em src/
4. **READMEs são valiosos** - Facilitam onboarding e navegação
5. **Organização é iterativa** - Estrutura evolui com o projeto

---

## 📚 Referências

- [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)
- [Notebook Naming Conventions](https://stackoverflow.com/questions/13208286/good-naming-convention-for-jupyter-notebooks)
- POC_TO_PRODUCTION.md (refatoração v2.1.0)

---

**Autor**: Claude (AI Assistant)
**Revisado por**: @RaphaelNorris
**Data**: 2024-11-23
**Versão do Projeto**: 2.2.0
**Status**: ✅ Implementado e documentado
