# Análise do Input do Streamlit

## Problema Identificado

O formulário do Streamlit está **INCOMPLETO**. Ele coleta apenas uma fração das features necessárias.

## Pipeline de Processamento

### 1. O que acontece quando o usuário preenche o formulário:

```
Input do Usuário (Formulário)
       ↓
process_pedidos() - Processa e enriquece os dados
       ↓
create_geometric_features() - Cria features derivadas
       ↓
Clustering (GMM) - Gera PROB_CLUSTER_*
       ↓
Modelo CatBoost - Predição final
```

### 2. Features que o modelo precisa (24 no total):

#### Diretas do formulário (usuário preenche):
- `QT_ARRANJO` ✅
- `QT_PEDIDA` ✅
- `VL_GRAMATURA` ✅
- `VL_COMPRIMENTO` ✅
- `VL_LARGURA` ✅
- `VL_MULTCOMP` ✅
- `CD_FACA` ✅ (usado para buscar VL_COMPLAMINA)

#### Features FALTANDO no formulário atual:
- `VL_REFUGOCLIENTE` ❌ **FALTANDO**
- `VL_PESOPECA` ❌ **FALTANDO**
- `VL_PESOCAIXA` ❌ **FALTANDO**
- `VL_AREALIQUIDAPECA` ❌ **FALTANDO**
- `VL_LARGPECA` ❌ **FALTANDO**
- `VL_COMPPECA` ❌ **FALTANDO**
- `VL_CONSUMO_COR_TOTAL` ❌ **FALTANDO** (soma dos consumos de cores)

#### Features geométricas (criadas automaticamente):
- `RAZAO_CHAPA_COMP_LARG` ✅ (VL_COMPRIMENTO / VL_LARGURA)
- `RAZAO_PECA_COMP_LARG` ✅ (VL_COMPPECA / VL_LARGPECA)
- `RAZAO_COMP_LARG` ✅
- `VOLUME_INTERNO` ✅ (criado automaticamente)
- `AREA_CHAPA` ✅ (VL_COMPRIMENTO * VL_LARGURA)
- `PECAS_POR_CHAPA` ✅ (VL_MULTCOMP * VL_MULTLARG)

#### Features da faca (buscadas automaticamente):
- `VL_COMPLAMINA` ✅ (vem de tb_facas usando CD_FACA)

#### Features dos clusters (calculadas automaticamente):
- `PROB_CLUSTER_0` ✅
- `PROB_CLUSTER_1` ✅
- `PROB_CLUSTER_4` ✅
- `PROB_CLUSTER_5` ✅

## Campos Faltando no Formulário

### CRÍTICOS (necessários para o modelo):

1. **VL_REFUGOCLIENTE** - Refugo do cliente (%)
2. **VL_PESOPECA** - Peso da peça (kg)
3. **VL_PESOCAIXA** - Peso da caixa (kg)
4. **VL_AREALIQUIDAPECA** - Área líquida da peça (mm²)
5. **VL_LARGPECA** - Largura da peça (mm)
6. **VL_COMPPECA** - Comprimento da peça (mm)
7. **Consumo de Cores**:
   - `QT_CONSUMOCOR1`
   - `QT_CONSUMOCOR2`
   - `QT_CONSUMOCOR3`
   - `QT_CONSUMOCOR4`
   - Ou criar campo único: `VL_CONSUMO_COR_TOTAL`

### Campos que o formulário atual coleta (mas podem ser opcionais):

- `QT_NRCORES` - Importante mas não está nas 24 features selecionadas
- `VL_MULTLARG` - Importante mas não está nas 24 features selecionadas
- Dimensões internas (usadas para criar VOLUME_INTERNO)

## Recomendações

### Opção 1: Formulário Completo (RECOMENDADA)
Adicionar TODOS os campos faltando ao formulário. O cliente preenche tudo.

### Opção 2: Valores Padrão Inteligentes
Para campos que o cliente não sabe, usar:
- Valores médios do histórico
- Cálculos baseados em outros campos
- Deixar como 0 (pior opção - vai afetar a precisão)

### Opção 3: Inferência de Campos
Criar lógica para calcular campos derivados:
- `VL_AREALIQUIDAPECA` = `VL_COMPPECA * VL_LARGPECA`
- `VL_PESOPECA` = `VL_GRAMATURA * VL_AREALIQUIDAPECA / 1000000`
- etc.

## Impacto da Falta de Features

Se features importantes faltarem, o modelo vai:
1. Assumir valor 0 (através da função `_align_columns` em inference.py)
2. Fazer predições com precisão REDUZIDA
3. Potencialmente dar resultados incorretos

## Solução Implementada

Vou criar um formulário COMPLETO com todos os campos necessários, organizados em seções lógicas.
