# 🔗 EDA - Análises Cruzadas

Esta pasta contém análises exploratórias que **relacionam múltiplas tabelas** do sistema ADAMI.

## 📁 Estrutura

| Notebook | Tabelas Relacionadas | Descrição |
|----------|---------------------|-----------|
| `10.0-rn-cross-pedidos-itens-20240101.ipynb` | tb_pedidos ↔ tb_itens | Relacionamento entre pedidos e catálogo de itens |
| `11.0-rn-cross-tarefcon-paradas-20240101.ipynb` | tb_tarefcon ↔ tb_paradas | Associação temporal de paradas com tarefas de produção |
| `12.0-rn-cross-tarefcon-itens-20240101.ipynb` | tb_tarefcon ↔ tb_itens | Análise de itens produzidos por tarefa |

## 🎯 Objetivo

Entender os **relacionamentos e inconsistências** entre diferentes tabelas do sistema:

1. **Chaves de Relacionamento**
   - Identificação de chaves primárias e estrangeiras
   - Validação de integridade referencial
   - Análise de cardinalidade

2. **Análise de Cobertura**
   - Registros órfãos
   - Missing links
   - Sobreposição de dados

3. **Comparação de Valores**
   - Diferenças entre tabelas relacionadas
   - Inconsistências de dados
   - Divergências temporais

4. **Padrões Temporais**
   - Sequência de eventos
   - Associação temporal
   - Janelas de tempo

## 📊 Análises Principais

### 10.0 - Pedidos × Itens

**Objetivo**: Comparar pedidos com catálogo de produtos

- Itens pedidos que não existem no catálogo
- Diferenças de especificações (pedido vs catálogo)
- Análise de mudanças de produtos ao longo do tempo

**Principais Descobertas**:
- Pedidos mantêm snapshot histórico das especificações
- Catálogo reflete estado atual
- Diferenças percentuais em dimensões

### 11.0 - TarefCon × Paradas

**Objetivo**: Associar paradas de máquinas com tarefas de produção

- Matching temporal de paradas com ordem de produção (OP)
- Análise de impacto de paradas na produção
- Inferência de relações pedido/item a partir de CD_OP

**Principais Descobertas**:
- Paradas podem ser associadas por janela temporal
- CD_OP contém informações não estruturadas (formato: PEDIDO/ITEM)
- Necessidade de limpeza e inferência de relações

### 12.0 - TarefCon × Itens

**Objetivo**: Analisar características dos itens produzidos

- Produtos mais produzidos
- Tempo de produção por tipo de item
- Complexidade de produção

## 🔍 Como Usar

1. **Pré-requisito**: Execute notebooks da pasta `01-eda-tables/` primeiro

2. Abra o Jupyter Lab:
   ```bash
   cd project_data_science/notebooks/02-eda-cross
   jupyter lab
   ```

3. Execute os notebooks na ordem numérica

## 💡 Insights Importantes

### Modelo de Dados

```
┌─────────────┐         ┌──────────────┐
│ tb_pedidos  │────────▶│  tb_itens    │
│             │         │  (catálogo)  │
└─────────────┘         └──────────────┘
       │
       │ (inferido via CD_OP)
       ▼
┌─────────────┐         ┌──────────────┐
│ tb_tarefcon │         │  tb_paradas  │
│             │◀────────│  (temporal)  │
└─────────────┘         └──────────────┘
```

### Descobertas Chave

1. **Integridade Referencial**: Nem sempre garantida
2. **Dados Temporais**: Úteis para inferir relações
3. **Snapshots**: Pedidos armazenam estado histórico
4. **Limpeza Necessária**: CD_OP precisa de parsing

## 🛠️ Funções Úteis

Estas análises geraram funções reutilizáveis em:
- `src/data/data_treatment.py`: Correção de relações TarefCon
- `src/analysis/data_processing.py`: Cálculo de diferenças
- `src/features/build_features.py`: Merge temporal

## 📝 Próximas Análises

Sugestões para futuras análises cruzadas:

- [ ] Clientes × Pedidos (análise de comportamento)
- [ ] Máquinas × Paradas (confiabilidade)
- [ ] Facas × Itens (associação de ferramentas)
- [ ] Pedidos × Paradas (impacto no prazo)

## 🔗 Veja Também

- **01-eda-tables/**: Análises de tabelas individuais
- **03-preprocessing/**: Limpeza baseada nos insights
- **04-production/**: Implementação das associações temporais
