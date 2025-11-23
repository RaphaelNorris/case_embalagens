beleza! aqui vai um checklist enxuto e acionável (o “to-do”) a partir do que o Mário explicou:

# To-dos a partir das respostas do Mário

## A. Escopo e filtros

* [ ] **Focar apenas nas máquinas** de **tipo 1 (C/V)** e **tipo 3 (Flexo)**.
* [ ] **Descartar eventos** com `CD_PARADAOUCONV = 0` (ex.: esteiras / fora de conversão).

## B. Padronização de chaves e campos

* [ ] **Preencher `CD_PEDIDO` e `CD_ITEM`** a partir de `CD_OP` (split por “/”) quando estiver faltando.
* [ ] **Normalizar `CD_PARADAOUCONV`** para inteiro/string sem “.0”.

## C. Associação de paradas à OP (lógica temporal)

* [ ] **Ordenar** por `CD_MAQUINA` e tempo (`DT_INICIO`/`DT_FIM`) e trabalhar por tempo **monotônico**.
* [ ] **Associar paradas (>=1)** à **OP anterior** quando estiverem **entre dois ajustes** (código **1**).
* [ ] Implementar **merge temporal (asof)**:

    * [ ] **Paradas sem `CD_OP`**: casar `DT_FIM` da parada com **próximo** `DT_INICIO` com `CD_OP` **na mesma máquina** dentro de uma **tolerância** (ex.: 30 min) e **herdar** a `CD_OP` encontrada.
    * [ ] **Produções sem `Ajuste` explícito**: se duas OPs consecutivas tiverem mesmo ferramental/cores, permitir **ausência de ajuste** sem penalizar.

## D. Casos “sem OP” e trocas de turno

* [ ] **Detectar eventos sem `CD_OP` perto das trocas de turno** (janelas centradas em **05:00, 13:00, 21:00** ± *t* min).
* [ ] Para esses casos, **tentar incorporar o tempo perdido** ao **evento seguinte** (ex.: Ajuste de código 1 que inicia logo após a troca).
* [ ] Sinalizar registros que **persistirem sem associação** após a regra (para **revisão manual**).

## E. Regras de negócio específicas

* [ ] **Ajuste (código 1)** encerra a OP anterior e **define a próxima**; usar isso como **âncora** de sequenciamento.
* [ ] **Paradas fora de qualquer janela `Início~Fim` de OP**: marcar como **erro de apontamento** ou **evento externo** (manutenção/feriado) e **excluir da análise de eficiência**.

## F. Enriquecimento e métricas

* [ ] Criar flags `NEAR_SHIFT_INICIO` e `NEAR_SHIFT_FIM` (± *t* min de 05:00, 13:00, 21:00).
* [ ] Calcular **tempo de parada “perdido”** que foi incorporado e **tempo que ficou sem OP** (para KPI de qualidade do apontamento).
* [ ] Produzir **relatório** por máquina/turno: % de paradas bem associadas, % “perto de troca”, % descartadas (código 0), casos para revisão.

## G. Qualidade de dados e validações

* [ ] Checar e corrigir **linhas com `DT_INICIO > DT_FIM`** ou tempos negativos.
* [ ] Garantir **tipos** (`datetime`, strings para chaves).
* [ ] **Deduplicar** e remover **NaT** nas chaves temporais antes de `merge_asof`.

## H. Entregáveis

* [ ] **Função simples** para **preencher `CD_PEDIDO`/`CD_ITEM` a partir de `CD_OP`**.
* [ ] **Função de inferência temporal de `CD_OP`** (asof, por máquina, com tolerância).
* [ ] **Função de detecção de “parada sem OP perto de troca de turno”** com sugestão de incorporação.
* [ ] **Notebook** com exemplos e **testes de amostra** (inclui logs dos casos tratados).
* [ ] **Dashboard** ou tabela final com **flags** e **KPIs**.

Se quiser, já te devolvo os 3 bloquinhos de código (A) preenchimento de pedido/item, (B) inferência de OP por asof e (C) detector “perto da troca de turno” — prontos pra colar no projeto.
