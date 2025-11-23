# 📊 EDA - Tabelas Individuais

Esta pasta contém análises exploratórias de dados (EDA) de **tabelas individuais** do banco de dados da ADAMI.

## 📁 Estrutura

Cada notebook nesta pasta analisa uma única tabela do sistema:

| Notebook | Tabela | Descrição |
|----------|--------|-----------|
| `00.0-rn-metadata-column-names-20240101.ipynb` | Metadata | Nomenclatura e dicionário de colunas |
| `01.0-rn-eda-general-20240101.ipynb` | Geral | Visão geral de todas as tabelas |
| `02.0-rn-eda-clientes-20240101.ipynb` | tb_clientes | Análise de clientes |
| `03.0-rn-eda-facas-20240101.ipynb` | tb_facas | Análise de facas/lâminas |
| `04.0-rn-eda-maquinas-20240101.ipynb` | tb_maquinas | Análise de máquinas de produção |
| `05.0-rn-eda-itens-20240101.ipynb` | tb_itens | Análise de itens/produtos |
| `06.0-rn-eda-pedidos-20240101.ipynb` | tb_pedidos | Análise de pedidos |
| `07.0-rn-eda-paradas-20240101.ipynb` | tb_paradas | Análise de paradas de máquinas |
| `08.0-rn-eda-tarefcon-20240101.ipynb` | tb_tarefcon | Análise de tarefas de produção |

## 🎯 Objetivo

Cada notebook segue a estrutura padrão de EDA:

1. **Carregamento de Dados**
   - Conexão com banco
   - Leitura de dados
   - Amostragem inicial

2. **Análise Descritiva**
   - Dimensões (linhas x colunas)
   - Tipos de dados
   - Valores nulos
   - Estatísticas descritivas

3. **Análise de Qualidade**
   - Valores ausentes
   - Duplicados
   - Outliers
   - Inconsistências

4. **Visualizações**
   - Distribuições
   - Correlações
   - Padrões temporais
   - Gráficos específicos do domínio

5. **Insights e Conclusões**
   - Principais descobertas
   - Problemas identificados
   - Recomendações

## 📊 Principais Entidades

### Clientes (tb_clientes)
Informações cadastrais dos clientes da ADAMI.

### Pedidos (tb_pedidos)
Pedidos de produção de embalagens feitos pelos clientes.

### Itens (tb_itens)
Catálogo de produtos/itens disponíveis.

### Máquinas (tb_maquinas)
Máquinas de produção (C/V, Flexo) e suas especificações.

### Facas (tb_facas)
Ferramentas de corte com status e comprimento de lâmina.

### Paradas (tb_paradas)
Registros de paradas não programadas de máquinas.

### TarefCon (tb_tarefcon)
Controle de tarefas de produção e associação com pedidos.

## 🔍 Como Usar

1. Abra o Jupyter Lab:
   ```bash
   cd project_data_science/notebooks/01-eda-tables
   jupyter lab
   ```

2. Selecione o notebook da tabela que deseja explorar

3. Execute célula por célula para entender os dados

## 💡 Dicas

- **Comece pelo 00**: O notebook de metadata ajuda a entender a nomenclatura
- **Sequencial**: Os notebooks foram numerados na ordem lógica de análise
- **Dados Sensíveis**: Configure o `.env` antes de executar conexões de banco

## 📝 Convenção de Nomenclatura

Todos os notebooks seguem o padrão:
```
##.#-autor-descricao-YYYYMMDD.ipynb
```

- `##.#`: Número sequencial
- `autor`: Iniciais (rn = Raphael Norris)
- `descricao`: Breve descrição
- `YYYYMMDD`: Data de criação

## 🔗 Próximos Passos

Após explorar as tabelas individuais, veja:
- **02-eda-cross/**: Análises cruzadas entre tabelas
- **03-preprocessing/**: Pré-processamento e limpeza
- **04-production/**: Notebooks de produção
