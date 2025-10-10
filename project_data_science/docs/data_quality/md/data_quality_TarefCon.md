<style>
    body { background-color: #ffffff; color: #111111; font-family: Arial, sans-serif; }
    h1, h2, h3 { color: #002060; }  /* azul escuro forte */
    
    table { border-collapse: collapse; width: 100%; margin-top: 10px; }
    th, td { border: 1px solid #444; padding: 8px; text-align: center; }
    
    th { background-color: #002060; color: #ffffff; }  /* cabeçalho azul escuro com letras brancas */
    td { color: #111111; background-color: #fafafa; } /* células cinza muito claro */
    
    .manter { color: #006400; font-weight: bold; }  /* verde escuro */
    .excluir { color: #b22222; font-weight: bold; } /* vermelho escuro */
    
    code { background-color: #f0f0f0; color: #002060; padding: 3px 5px; border-radius: 4px; font-weight: bold; }
    </style>
    

# Relatório de Análise de Qualidade de Dados

## Informações Gerais
- **Tabela:** `dbo.TarefCon`
- **Data/Hora:** 2025-09-24 13:33:49
- **Total de Registros:** 1604727
- **Total de Colunas:** 44
- **Autor:** Raphael Norris

---

## Filtros Aplicados
- **DataCriacao** >= `2022-01-01`

---

## Query Executada
```sql
SELECT * FROM dbo.TarefCon WHERE DataCriacao >= `2022-01-01`
```


---

## Resumo da Análise

| Métrica | Valor |
|---------|-------|
| Total de Colunas | 44 |
| Colunas para Manter | 32 |
| Colunas para Excluir | 12 |
| Percentual de Exclusão | 27.3% |

---

## Colunas Sugeridas para Exclusão

| # | Coluna | Motivos |
|---|--------|---------|
| 1 | `Operacao` | MUITOS NULOS (100.0%) |
| 2 | `Obs1` | STRINGS VAZIAS (85.2%) |
| 3 | `Obs2` | STRINGS VAZIAS (91.6%) |
| 4 | `AcaoCorretivaTomada` | MUITOS NULOS (99.7%) |
| 5 | `Consolidado` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 6 | `CaixasSemCola` | MUITOS NULOS (99.3%) |
| 7 | `SkipFeed` | MUITOS ZEROS (100.0%) |
| 8 | `IDSecaoMaquinaParada` | MUITOS NULOS (90.8%) | MUITOS ZEROS (99.0%) |
| 9 | `ObsFila1` | MUITOS NULOS (95.1%) |
| 10 | `ObsFila2` | MUITOS NULOS (98.8%) |
| 11 | `PriorizarPaleteAutomacaoEsteira` | MUITOS NULOS (97.2%) | VALOR ÚNICO (False) |
| 12 | `idCodigoDestinoAutomacaoEsteira` | MUITOS NULOS (99.6%) |

---

## Análise Detalhada de Todas as Colunas

| Coluna | Ação | Nulos (%) | Valores Únicos | Variância (%) | Zeros (%) | Vazias (%) | Tipo | Motivos |
|--------|------|-----------|----------------|---------------|-----------|------------|------|---------|
| `Maquina` | <span class='manter'>MANTER</span> | 0.0% | 34 | 0.0% | 0% | 0.0% | `object` | OK |
| `Tarefa` | <span class='manter'>MANTER</span> | 0.0% | 1604727 | 100.0% | 0.0% | 0% | `int64` | OK |
| `FlagParada` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 19.9% | 0% | `int64` | OK |
| `CodigoParadaOuConv` | <span class='manter'>MANTER</span> | 19.9% | 39 | 0.0% | 0.9% | 0% | `float64` | OK |
| `Turma` | <span class='manter'>MANTER</span> | 0.0% | 3 | 0.0% | 0% | 0.0% | `object` | OK |
| `OP` | <span class='manter'>MANTER</span> | 4.1% | 255746 | 16.6% | 0% | 0.0% | `object` | OK |
| `Pedido` | <span class='manter'>MANTER</span> | 80.1% | 249305 | 78.0% | 0% | 0.0% | `object` | OK |
| `Item` | <span class='manter'>MANTER</span> | 80.1% | 14911 | 4.7% | 0% | 0.0% | `object` | OK |
| `Reprogramacao` | <span class='manter'>MANTER</span> | 80.1% | 5 | 0.0% | 0.0% | 0% | `float64` | OK |
| `Passagens` | <span class='manter'>MANTER</span> | 80.1% | 4 | 0.0% | 0.0% | 0% | `float64` | OK |
| `Operacao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Arranjo` | <span class='manter'>MANTER</span> | 80.1% | 17 | 0.0% | 0.0% | 0% | `float64` | OK |
| `Gramatura` | <span class='manter'>MANTER</span> | 80.1% | 733 | 0.2% | 0.0% | 0% | `float64` | OK |
| `QuantidadeProgramada` | <span class='manter'>MANTER</span> | 80.1% | 25787 | 8.1% | 0.3% | 0% | `float64` | OK |
| `ChapasAlimentadas` | <span class='manter'>MANTER</span> | 80.1% | 19956 | 6.2% | 0.0% | 0% | `float64` | OK |
| `QuantidadeProduzida` | <span class='manter'>MANTER</span> | 80.1% | 25091 | 7.8% | 0.4% | 0% | `float64` | OK |
| `QuantidadeAjuste` | <span class='manter'>MANTER</span> | 80.1% | 486 | 0.2% | 55.6% | 0% | `float64` | OK |
| `DuracaoPrevista` | <span class='manter'>MANTER</span> | 82.2% | 1747 | 0.6% | 0.6% | 0% | `float64` | OK |
| `Inicio` | <span class='manter'>MANTER</span> | 0.0% | 1306386 | 81.4% | 0% | 0% | `datetime64[ns]` | OK |
| `Fim` | <span class='manter'>MANTER</span> | 0.0% | 1477522 | 92.1% | 0% | 0% | `datetime64[ns]` | OK |
| `Obs1` | <span class='excluir'>EXCLUIR</span> | 23.4% | 78349 | 6.4% | 0% | 85.2% | `object` | STRINGS VAZIAS (85.2%) |
| `Obs2` | <span class='excluir'>EXCLUIR</span> | 27.6% | 7 | 0.0% | 0% | 91.6% | `object` | STRINGS VAZIAS (91.6%) |
| `AcaoCorretivaTomada` | <span class='excluir'>EXCLUIR</span> | 99.7% | 910 | 21.0% | 0% | 1.4% | `object` | MUITOS NULOS (99.7%) |
| `Consolidado` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `DiaDaTurma` | <span class='manter'>MANTER</span> | 0.0% | 1359 | 0.1% | 0% | 0% | `datetime64[ns]` | OK |
| `IDCliente` | <span class='manter'>MANTER</span> | 80.1% | 1047 | 0.3% | 0.0% | 0% | `float64` | OK |
| `Usuario` | <span class='manter'>MANTER</span> | 5.3% | 114 | 0.0% | 0.0% | 0% | `float64` | OK |
| `DataCriacao` | <span class='manter'>MANTER</span> | 0.0% | 1591039 | 99.1% | 0% | 0% | `datetime64[ns]` | OK |
| `UsuarioUltAlteracao` | <span class='manter'>MANTER</span> | 78.1% | 129 | 0.0% | 0.0% | 0% | `float64` | OK |
| `DataUltimaAlteracao` | <span class='manter'>MANTER</span> | 0.0% | 1595784 | 99.4% | 0% | 0% | `datetime64[ns]` | OK |
| `CaixasSemCola` | <span class='excluir'>EXCLUIR</span> | 99.3% | 511 | 4.4% | 0.0% | 0% | `float64` | MUITOS NULOS (99.3%) |
| `OrigemRegistro` | <span class='manter'>MANTER</span> | 0.8% | 3 | 0.0% | 5.7% | 0% | `float64` | OK |
| `DescOrigemRegistro` | <span class='manter'>MANTER</span> | 0.0% | 4 | 0.0% | 0% | 0.0% | `object` | OK |
| `SkipFeed` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 100.0% | 0% | `int64` | MUITOS ZEROS (100.0%) |
| `OPOndulada` | <span class='manter'>MANTER</span> | 89.6% | 49968 | 29.9% | 0% | 0.0% | `object` | OK |
| `TarefaProducao` | <span class='manter'>MANTER</span> | 23.9% | 261931 | 21.5% | 0.0% | 0% | `float64` | OK |
| `RefileDiretoPrensa` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 1.5% | 0% | `bool` | OK |
| `Duracao` | <span class='manter'>MANTER</span> | 0.0% | 526 | 0.0% | 0.0% | 0% | `int64` | OK |
| `IDSecaoMaquinaParada` | <span class='excluir'>EXCLUIR</span> | 90.8% | 19 | 0.0% | 99.0% | 0% | `float64` | MUITOS NULOS (90.8%) | MUITOS ZEROS (99.0%) |
| `Faca` | <span class='manter'>MANTER</span> | 86.3% | 2407 | 1.1% | 0% | 0.9% | `object` | OK |
| `ObsFila1` | <span class='excluir'>EXCLUIR</span> | 95.1% | 2204 | 2.8% | 0% | 62.2% | `object` | MUITOS NULOS (95.1%) |
| `ObsFila2` | <span class='excluir'>EXCLUIR</span> | 98.8% | 2 | 0.0% | 0% | 19.9% | `object` | MUITOS NULOS (98.8%) |
| `PriorizarPaleteAutomacaoEsteira` | <span class='excluir'>EXCLUIR</span> | 97.2% | 1 | 0.0% | 0% | 0.0% | `object` | MUITOS NULOS (97.2%) | VALOR ÚNICO (False) |
| `idCodigoDestinoAutomacaoEsteira` | <span class='excluir'>EXCLUIR</span> | 99.6% | 2 | 0.0% | 0.0% | 0% | `float64` | MUITOS NULOS (99.6%) |

---

## Critérios de Exclusão Utilizados

- Muitos Nulos: > 90% de valores nulos
- Valor Único: coluna possui apenas 1 valor único
- Muitos Zeros: > 80% de valores zero (para colunas numéricas)
- Strings Vazias: > 80% de strings vazias (para colunas de texto)

Colunas que não atendem a esses critérios são mantidas.
