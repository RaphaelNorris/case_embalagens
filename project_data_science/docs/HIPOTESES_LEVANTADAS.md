# Hipóteses Levantadas - Próximos Passos

## 📋 Objetivo deste Documento

Este documento lista **hipóteses identificadas durante as análises** que, se validadas, podem:
- ✅ Melhorar significativamente a acurácia do modelo
- ✅ Revelar insights operacionais importantes
- ✅ Gerar economia de custos ou aumento de produtividade
- ✅ Guiar decisões estratégicas da Adami

---

## 1. HIPÓTESES SOBRE PRODUTIVIDADE

### H1.1: Ondas do Papelão (B, C, D, BC, DC)
**Hipótese**: Tipos de onda específicos impactam diretamente a produtividade, especialmente combinações (BC, DC)

**Observação Inicial**:
- Dados mostram tipos: B, C, D, BC, DC
- Onda B (maior): pode ser mais lenta de processar
- Onda C (média): mais comum, produtividade média
- Combinações (BC, DC): podem exigir setups especiais

**Como Validar**:
```
1. Análise estatística: ANOVA entre tipos de onda vs produtividade
2. Segmentar modelo: treinar um modelo por tipo de onda
3. Consultar operadores: "Onda B é realmente mais lenta?"
```

**Impacto se Verdadeiro**:
- Precificação diferenciada por tipo de onda
- Alocação de máquinas específicas para cada tipo
- Melhoria de acurácia: +5-10% ROC AUC

**Prioridade**: 🔴 ALTA

---

### H1.2: Economia de Escala Não-Linear
**Hipótese**: Existe um "ponto ótimo" de quantidade (não apenas "quanto maior, melhor")

**Observação Inicial**:
- QT_PEDIDA é a feature mais importante (0.0276)
- Mas relação pode não ser linear
- Pedidos MUITO grandes podem ter problemas logísticos

**Como Validar**:
```
1. Gráfico: Produtividade vs QT_PEDIDA (scatter plot)
2. Identificar curva (linear, logarítmica, ou curva em U?)
3. Testar features polinomiais: QT_PEDIDA², QT_PEDIDA³
4. Segmentar: pequeno (<1000), médio (1000-5000), grande (>5000)
```

**Impacto se Verdadeiro**:
- Recomendar "lote ótimo" para clientes
- Evitar pedidos muito pequenos (custo/benefício)
- Negociar mínimos de pedido

**Prioridade**: 🟡 MÉDIA

---

### H1.3: Peso da Peça Tem Threshold Crítico
**Hipótese**: Peças acima de certo peso (ex: >100g) têm queda abrupta de produtividade

**Observação Inicial**:
- VL_PESOPECA está no top 10 de importância
- Máquinas podem ter limitação física
- Papelão mais pesado = ajustes de máquina

**Como Validar**:
```
1. Histograma: Distribuição de VL_PESOPECA por classe (ALTA/BAIXA)
2. Identificar threshold visual (onde muda a distribuição?)
3. Testar feature binária: FL_PESADO = 1 se VL_PESOPECA > threshold
4. Consultar especificações técnicas das máquinas
```

**Impacto se Verdadeiro**:
- Feature nova: FL_PESADO (melhora modelo)
- Alerta automático: "Pedido pesado, alocar máquina X"
- Planejamento de manutenção preventiva

**Prioridade**: 🟡 MÉDIA

---

### H1.4: Múltiplas Cores Tem Custo Exponencial
**Hipótese**: Cada cor adicional não reduz linearmente a produtividade, mas exponencialmente

**Observação Inicial**:
- QT_NRCORES varia de 0 a 8+
- 1→2 cores: impacto pequeno
- 4+ cores: impacto grande (hipótese)

**Como Validar**:
```
1. Boxplot: Produtividade por número de cores (0, 1, 2, 3, 4, 5+)
2. Testar features: QT_NRCORES², log(QT_NRCORES)
3. Segmentar: sem cor, mono, bicromia, policromia
4. Calcular tempo de setup por cor (dados de máquina)
```

**Impacto se Verdadeiro**:
- Precificação não-linear por cor
- Agrupar pedidos por número de cores (batching)
- Recomendar redução de cores para clientes sensíveis a prazo

**Prioridade**: 🟡 MÉDIA

---

### H1.5: Refugo Cliente é Proxy de Complexidade
**Hipótese**: VL_REFUGOCLIENTE alto não é só desperdício, é indicador de pedido complexo/crítico

**Observação Inicial**:
- VL_REFUGOCLIENTE está no top 3 de importância
- Refugo alto pode significar:
  - Cliente exigente (inspeção rigorosa)
  - Produto frágil/difícil
  - Tolerância baixa de erro

**Como Validar**:
```
1. Correlação: VL_REFUGOCLIENTE vs outras features de complexidade (QT_NRCORES, FL_TESTE)
2. Cluster analysis: Pedidos com alto refugo formam cluster específico?
3. Entrevista: "Por que alguns clientes têm refugo alto?"
```

**Impacto se Verdadeiro**:
- Criar índice de "complexidade" que combina refugo + outras features
- Alocar operadores mais experientes para alto refugo
- SLA diferenciado para clientes de alto refugo

**Prioridade**: 🟢 BAIXA (mais insight que ação)

---

## 2. HIPÓTESES SOBRE CLUSTERS

### H2.1: Clusters Têm "Personalidades" Distintas
**Hipótese**: Cada cluster representa um arquétipo de pedido com características operacionais únicas

**Observação Inicial**:
- Modelo GMM encontrou 4 clusters (CV) e 7 (Flexo)
- PROB_CLUSTER_X está no top 10 de features

**Como Validar**:
```
1. Profiling de clusters:
   - Cluster 0: Média de QT_PEDIDA, QT_NRCORES, VL_GRAMATURA, etc.
   - Cluster 1: ...
   - Identificar "persona" (ex: "Pedidos Pequenos Simples", "Grandes Complexos")

2. Visualizar: PCA 2D colorido por cluster + produtividade

3. Calcular: % de ALTA produtividade por cluster
```

**Impacto se Verdadeiro**:
- Nomear clusters: "Cluster Express", "Cluster Premium", etc.
- Roteamento inteligente: Cluster X → Máquina Y
- SLA por cluster: Cluster simples = 2 dias, complexo = 5 dias

**Prioridade**: 🔴 ALTA (alto valor operacional)

---

### H2.2: Clusters Evoluem no Tempo
**Hipótese**: Distribuição de clusters muda ao longo do ano (sazonalidade de tipos de pedido)

**Observação Inicial**:
- Apenas dados de 2024
- Possível sazonalidade (ex: Natal = mais caixas de presente?)

**Como Validar**:
```
1. Gráfico de linha: % de cada cluster por mês (Jan-Nov 2024)
2. Testar sazonalidade: Dezembro tem mais Cluster X?
3. Se dados de 2022-2023 disponíveis: comparar ano a ano
```

**Impacto se Verdadeiro**:
- Planejamento de capacidade sazonal
- Retreinar modelo trimestralmente (não apenas mensalmente)
- Antecipar demanda por tipo de pedido

**Prioridade**: 🟡 MÉDIA

---

### H2.3: Transições Entre Clusters Custam Mais
**Hipótese**: Produzir pedidos de clusters diferentes sequencialmente reduz produtividade (tempo de setup)

**Observação Inicial**:
- Não temos dados de sequência de pedidos (ainda)
- Mas setup de máquina varia por tipo de pedido

**Como Validar**:
```
1. Coletar dados: CD_OP anterior ao atual (sequência)
2. Feature nova: FL_MESMO_CLUSTER = 1 se cluster atual == cluster anterior
3. Testar: Produtividade quando FL_MESMO_CLUSTER=1 vs 0
```

**Impacto se Verdadeiro**:
- Algoritmo de sequenciamento: agrupar pedidos do mesmo cluster
- Redução de 10-20% em tempo de setup
- Ganho de capacidade sem investimento

**Prioridade**: 🔴 ALTA (se dados de sequência existirem)

---

## 3. HIPÓTESES SOBRE FEATURES

### H3.1: Razões Geométricas São Mais Importantes que Valores Absolutos
**Hipótese**: Proporção comprimento/largura importa mais que comprimento isolado

**Observação Inicial**:
- RAZAO_COMP_LARG e RAZAO_INTERNA foram criadas
- Mas VL_COMPRIMENTO também está no top 10

**Como Validar**:
```
1. Feature importance: Comparar RAZAO_COMP_LARG vs VL_COMPRIMENTO
2. Criar mais razões:
   - RAZAO_VOLUME_AREA = VOLUME_INTERNO / AREA_CHAPA
   - RAZAO_PESO_VOLUME = VL_PESOPECA / VOLUME_INTERNO (densidade)
3. Retreinar sem valores absolutos, apenas razões
```

**Impacto se Verdadeiro**:
- Simplificar modelo (menos features)
- Insights: "Caixas quadradas são 20% mais produtivas que retangulares"
- Recomendações de design para clientes

**Prioridade**: 🟢 BAIXA (otimização)

---

### H3.2: Features Temporais Estão Ausentes (e Importam)
**Hipótese**: Dia da semana, mês, feriados impactam produtividade

**Observação Inicial**:
- Não usamos DT_ENTREGAORIGINAL como feature (apenas filtro)
- Segunda-feira pode ter produtividade diferente de sexta

**Como Validar**:
```
1. Criar features temporais:
   - DIA_SEMANA (0-6)
   - MES (1-12)
   - FL_INICIO_MES, FL_FIM_MES
   - FL_FERIADO (requer calendário)

2. Retreinar modelo incluindo essas features

3. Verificar importância
```

**Impacto se Verdadeiro**:
- Planejamento: evitar pedidos complexos em segundas-feiras
- Detecção de fadiga de fim de semana
- Ajuste de SLA por dia da semana

**Prioridade**: 🟡 MÉDIA

---

### H3.3: Interações Entre Features São Não-Capturadas
**Hipótese**: QT_PEDIDA × QT_NRCORES (quantidade × cores) tem efeito combinado forte

**Observação Inicial**:
- CatBoost captura interações automaticamente, mas pode não ser suficiente
- Features de interação explícitas podem ajudar

**Como Validar**:
```
1. Criar features de interação:
   - QT_PEDIDA_X_CORES = QT_PEDIDA × QT_NRCORES
   - AREA_X_GRAMATURA = AREA_CHAPA × VL_GRAMATURA
   - MULT_X_ARRANJO = (VL_MULTCOMP × VL_MULTLARG) × QT_ARRANJO

2. Testar importância dessas features

3. Comparar modelo com/sem interações
```

**Impacto se Verdadeiro**:
- Melhoria de acurácia: +2-5% ROC AUC
- Insights: "Pedidos grandes COM muitas cores são especialmente problemáticos"

**Prioridade**: 🟡 MÉDIA

---

## 4. HIPÓTESES SOBRE DADOS AUSENTES

### H4.1: Missing Data Não É Aleatório (MNAR)
**Hipótese**: Valores ausentes em VL_COMPLAMINA, VL_REFUGOCLIENTE têm significado (não é erro)

**Observação Inicial**:
- 15-20% de missing data em algumas features
- Pode ser:
  - Não aplicável (ex: sem laminação → VL_COMPLAMINA = NaN)
  - Não medido (cliente não especificou refugo)

**Como Validar**:
```
1. Criar flags: FL_MISSING_COMPLAMINA, FL_MISSING_REFUGO
2. Testar: Produtividade quando FL_MISSING_X=1 vs 0
3. Análise: Pedidos com missing formam cluster específico?
```

**Impacto se Verdadeiro**:
- Não preencher com mediana, mas com 0 + flag
- Feature FL_MISSING pode ser preditiva
- Melhor tratamento de NaN = melhor modelo

**Prioridade**: 🟡 MÉDIA

---

### H4.2: Ausência de VL_REFUGOCLIENTE Significa "Cliente Não Exigente"
**Hipótese**: Se cliente não especifica refugo aceito, é sinal de menor rigor/complexidade

**Observação Inicial**:
- VL_REFUGOCLIENTE tem muitos NaN
- Hipótese: NaN ≠ 0 (zero é explícito, NaN é omissão)

**Como Validar**:
```
1. Comparar produtividade:
   - Grupo A: VL_REFUGOCLIENTE = 0 (especificou zero)
   - Grupo B: VL_REFUGOCLIENTE = NaN (não especificou)
   - Grupo C: VL_REFUGOCLIENTE > 0 (especificou valor)

2. Testar hipótese: Grupo B tem MAIOR produtividade que A e C?
```

**Impacto se Verdadeiro**:
- Tratamento especial: NaN → flag "cliente flexível"
- Priorizar pedidos "flexíveis" quando capacidade baixa

**Prioridade**: 🟢 BAIXA

---

## 5. HIPÓTESES SOBRE MODELAGEM

### H5.1: Threshold 0.70 Não É Ótimo
**Hipótese**: Threshold de probabilidade atual (0.70) pode não maximizar valor de negócio

**Observação Inicial**:
- Threshold fixo = 0.70 (escolha arbitrária)
- Custo de falso positivo ≠ custo de falso negativo

**Como Validar**:
```
1. Calcular custos reais:
   - Custo FP: Prever ALTA, é BAIXA → Atraso de R$ X
   - Custo FN: Prever BAIXA, é ALTA → Oportunidade perdida R$ Y

2. Curva de custo: Variar threshold de 0.5 a 0.9
   - Calcular custo total para cada threshold
   - Encontrar threshold que minimiza custo

3. Testar threshold por cluster (cada cluster pode ter ótimo diferente)
```

**Impacto se Verdadeiro**:
- Threshold ótimo = R$ Z economizados/ano
- Thresholds dinâmicos por contexto
- Maximizar valor, não apenas acurácia

**Prioridade**: 🔴 ALTA (impacto financeiro direto)

---

### H5.2: Modelo de Regressão Seria Mais Útil
**Hipótese**: Prever valor exato de produtividade (peças/hora) tem mais valor que classificação binária

**Observação Inicial**:
- Modelo atual: ALTA/BAIXA (binário)
- Mas usuários podem querer: "Quanto tempo vai levar?"

**Como Validar**:
```
1. Treinar XGBoost Regressor (target = produtividade contínua)
2. Métricas: MAE, RMSE, R²
3. Comparar utilidade:
   - Binário: "Será ALTA ou BAIXA?"
   - Regressão: "Produzirá 1200 peças/hora"

4. A/B test com usuários: qual preferem?
```

**Impacto se Verdadeiro**:
- Estimativa de tempo de produção mais precisa
- Precificação dinâmica baseada em tempo estimado
- Planejamento de capacidade mais granular

**Prioridade**: 🔴 ALTA (roadmap próximos 3 meses)

---

### H5.3: Ensemble de Modelos Supera Modelo Único
**Hipótese**: Combinar CatBoost + XGBoost + LightGBM melhora acurácia

**Observação Inicial**:
- Apenas CatBoost sendo usado
- Diferentes algoritmos capturam padrões diferentes

**Como Validar**:
```
1. Treinar 3 modelos: CatBoost, XGBoost, LightGBM
2. Ensemble:
   - Voting: Média das probabilidades
   - Stacking: Meta-modelo em cima dos 3

3. Comparar ROC AUC: Ensemble vs Melhor Individual
```

**Impacto se Verdadeiro**:
- Melhoria de +2-5% ROC AUC
- Mais robusto a outliers
- Custo: 3x tempo de treinamento/inferência

**Prioridade**: 🟡 MÉDIA (otimização)

---

## 6. HIPÓTESES SOBRE OPERAÇÕES

### H6.1: Operadores Experientes Compensam Pedidos Complexos
**Hipótese**: Mesma especificação de pedido tem produtividade diferente dependendo do operador

**Observação Inicial**:
- Não temos CD_OPERADOR nos dados
- Experiência humana não está no modelo

**Como Validar**:
```
1. Coletar dados: CD_OPERADOR ou CD_TURMA
2. Feature nova: EXPERIENCIA_OPERADOR (anos de casa?)
3. Testar: Mesmos pedidos (mesmo cluster) com operadores diferentes
```

**Impacto se Verdadeiro**:
- Modelo separado por nível de experiência
- Alocação inteligente: novatos → pedidos simples, veteranos → complexos
- Programa de mentoria focado em clusters problemáticos

**Prioridade**: 🔴 ALTA (se dados disponíveis)

---

### H6.2: Manutenção Preventiva Reduz Produtividade Temporariamente
**Hipótese**: Após manutenção, máquina tem período de "aquecimento" com menor produtividade

**Observação Inicial**:
- Não temos dados de manutenção
- Mas pode explicar variações não-capturadas

**Como Validar**:
```
1. Cruzar com dados de manutenção (se existirem)
2. Feature: DIAS_DESDE_MANUTENCAO
3. Testar: Produtividade vs DIAS_DESDE_MANUTENCAO (curva de aprendizado?)
```

**Impacto se Verdadeiro**:
- Evitar pedidos críticos logo após manutenção
- Agendar manutenção considerando pipeline de pedidos
- Feature nova melhora modelo

**Prioridade**: 🟡 MÉDIA (se dados existirem)

---

### H6.3: Batching de Pedidos Similares Aumenta Produtividade
**Hipótese**: Produzir pedidos similares em sequência (mesmo cluster) reduz tempo de setup

**Observação Inicial**:
- Já mencionado em H2.3
- Mas aqui foco é em operação, não modelagem

**Como Validar**:
```
1. Experimento controlado:
   - Semana 1: Produção normal (sequência aleatória)
   - Semana 2: Produção agrupada (mesmo cluster sequencial)
   - Semana 3: Volta ao normal

2. Comparar: Produtividade média semanal

3. Medir: Tempo de setup entre pedidos
```

**Impacto se Verdadeiro**:
- Algoritmo de sequenciamento (scheduling)
- Ganho de 10-15% em capacidade
- ROI alto (sem investimento em hardware)

**Prioridade**: 🔴 ALTA (teste rápido, alto impacto)

---

## 7. HIPÓTESES SOBRE CLIENTES

### H7.1: Clientes Recorrentes São Mais Produtivos
**Hipótese**: Pedidos de clientes que já fizeram pedidos similares antes são mais produtivos (aprendizado)

**Observação Inicial**:
- Não temos CD_CLIENTE nos dados
- Mas cliente recorrente = familiaridade com especificação

**Como Validar**:
```
1. Adicionar: CD_CLIENTE
2. Feature: QT_PEDIDOS_ANTERIORES_CLIENTE
3. Feature: FL_CLIENTE_RECORRENTE (>5 pedidos)
4. Testar: Produtividade de recorrentes vs novos
```

**Impacto se Verdadeiro**:
- Descontos para clientes recorrentes (win-win)
- Onboarding especial para clientes novos
- Feature preditiva valiosa

**Prioridade**: 🟡 MÉDIA

---

### H7.2: Clientes de Certos Setores Têm Padrões Específicos
**Hipótese**: E-commerce, alimentos, cosméticos têm características de pedidos distintas

**Observação Inicial**:
- Não temos SETOR_CLIENTE
- Mas e-commerce pode ter padrão (caixas pequenas, muita cor)

**Como Validar**:
```
1. Adicionar: SETOR_CLIENTE (manual ou via CNAE)
2. Cluster analysis por setor
3. Produtividade média por setor
```

**Impacto se Verdadeiro**:
- Marketing segmentado
- Especialização de máquinas por setor
- Modelo específico por vertical

**Prioridade**: 🟢 BAIXA (requer dados externos)

---

## 8. HIPÓTESE META

### H8.1: Explicabilidade Melhora Adoção do Sistema
**Hipótese**: Operadores confiam mais no sistema quando veem TOP 5 features (SHAP) do que apenas a predição

**Observação Inicial**:
- SHAP já implementado
- Mas não sabemos se usuários valorizam

**Como Validar**:
```
1. A/B test:
   - Grupo A: Vê apenas "ALTA/BAIXA" + probabilidade
   - Grupo B: Vê "ALTA/BAIXA" + TOP 5 features + SHAP

2. Métricas:
   - % de predições que usuário seguiu
   - NPS (satisfação)
   - Tempo para tomar decisão

3. Entrevistas qualitativas
```

**Impacto se Verdadeiro**:
- Manter SHAP (custo computacional vale a pena)
- Investir em explicabilidade avançada (counterfactuals)
- Treinamento focado em interpretar SHAP

**Prioridade**: 🟡 MÉDIA (UX)

---

## RESUMO: TOP 10 HIPÓTESES PRIORITÁRIAS

| # | Hipótese | Prioridade | Esforço | Impacto | Quick Win? |
|---|----------|------------|---------|---------|------------|
| 1 | **H5.1**: Threshold ótimo por custo de negócio | 🔴 ALTA | Baixo | Alto | ✅ SIM |
| 2 | **H2.1**: Clusters têm "personalidades" distintas | 🔴 ALTA | Baixo | Alto | ✅ SIM |
| 3 | **H6.3**: Batching de pedidos similares | 🔴 ALTA | Médio | Muito Alto | ⚠️ Requer experimento |
| 4 | **H1.1**: Ondas de papelão (B, C, D, BC, DC) | 🔴 ALTA | Baixo | Alto | ✅ SIM |
| 5 | **H5.2**: Modelo de regressão (peças/hora exato) | 🔴 ALTA | Alto | Alto | ❌ NÃO (longo prazo) |
| 6 | **H6.1**: Experiência do operador | 🔴 ALTA | Médio | Alto | ⚠️ Se dados existirem |
| 7 | **H2.3**: Custo de transição entre clusters | 🔴 ALTA | Médio | Alto | ⚠️ Se dados existirem |
| 8 | **H1.2**: Economia de escala não-linear | 🟡 MÉDIA | Baixo | Médio | ✅ SIM |
| 9 | **H3.2**: Features temporais (dia da semana, mês) | 🟡 MÉDIA | Baixo | Médio | ✅ SIM |
| 10 | **H2.2**: Clusters evoluem no tempo (sazonalidade) | 🟡 MÉDIA | Baixo | Médio | ✅ SIM |

---

## PRÓXIMOS PASSOS RECOMENDADOS

### Fase 1: Análises Rápidas (1-2 semanas)
```
✅ H5.1: Calcular threshold ótimo
✅ H2.1: Profiling de clusters
✅ H1.1: Análise de ondas de papelão
✅ H1.2: Curva de quantidade vs produtividade
✅ H3.2: Adicionar features temporais
✅ H2.2: Sazonalidade de clusters
```

### Fase 2: Coleta de Dados Adicionais (2-4 semanas)
```
⚠️ H6.1: Adicionar CD_OPERADOR ou experiência
⚠️ H2.3: Adicionar CD_OP_ANTERIOR (sequência)
⚠️ H6.2: Cruzar com dados de manutenção
⚠️ H7.1: Adicionar CD_CLIENTE e histórico
```

### Fase 3: Experimentos Operacionais (1-2 meses)
```
🧪 H6.3: Teste de batching (semanas alternadas)
🧪 H8.1: A/B test de explicabilidade
```

### Fase 4: Melhorias de Modelo (2-3 meses)
```
🔬 H5.2: Treinar modelo de regressão
🔬 H5.3: Testar ensemble
🔬 H3.3: Adicionar features de interação
🔬 H4.1: Melhorar tratamento de missing data
```

---

## COMO USAR ESTE DOCUMENTO

### Para Apresentação (PPT)
- **Slide 1**: "Identificamos 20+ hipóteses durante as análises"
- **Slide 2**: Mostrar TOP 10 (tabela acima)
- **Slide 3**: Destacar 3-5 hipóteses de maior impacto (H5.1, H6.3, H2.1)
- **Slide 4**: Próximos passos (Fases 1-4)

### Para Discussão com Time
- Validar hipóteses com conhecimento de domínio
- Priorizar baseado em viabilidade de dados
- Planejar experimentos controlados

### Para Roadmap Técnico
- Fase 1 = Quick Wins (apresentar resultados em 1 mês)
- Fase 2 = Dependente de disponibilidade de dados
- Fase 3-4 = Longo prazo (após validação do piloto)

---

**Última atualização**: Novembro 2024
**Responsável**: Time de IA AMCOM + Adami
