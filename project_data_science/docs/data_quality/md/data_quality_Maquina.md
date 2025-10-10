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
- **Tabela:** `dbo.Maquina`
- **Data/Hora:** 2025-09-24 13:33:49
- **Total de Registros:** 50
- **Total de Colunas:** 83
- **Autor:** Raphael Norris

---

## Filtros Aplicados
- Nenhum filtro aplicado

---

## Query Executada
```sql
SELECT * FROM dbo.Maquina
```

---

## Resumo da Análise

| Métrica | Valor |
|---------|-------|
| Total de Colunas | 83 |
| Colunas para Manter | 29 |
| Colunas para Excluir | 54 |
| Percentual de Exclusão | 65.1% |

---

## Colunas Sugeridas para Exclusão

| # | Coluna | Motivos |
|---|--------|---------|
| 1 | `Facoes` | MUITOS ZEROS (96.0%) |
| 2 | `LargUtilMax` | MUITOS ZEROS (96.0%) |
| 3 | `LargMinChapa` | MUITOS ZEROS (96.0%) |
| 4 | `LargMaxChapa` | MUITOS ZEROS (96.0%) |
| 5 | `CompMinChapa` | MUITOS NULOS (96.0%) | VALOR ÚNICO (620.0) |
| 6 | `CompMaxChapa` | MUITOS NULOS (96.0%) | VALOR ÚNICO (4000.0) |
| 7 | `RefiloMin` | MUITOS NULOS (96.0%) |
| 8 | `RefiloMax` | MUITOS NULOS (96.0%) | VALOR ÚNICO (176.0) |
| 9 | `Facas` | MUITOS NULOS (96.0%) | VALOR ÚNICO (7.0) |
| 10 | `PermiteMisturarFerramentas` | MUITOS ZEROS (96.0%) |
| 11 | `idTipoVincoPadrao` | MUITOS NULOS (96.0%) | VALOR ÚNICO (16.0) |
| 12 | `TearTape` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 13 | `ResinaInterna` | MUITOS ZEROS (95.3%) |
| 14 | `ResinaExterna` | MUITOS ZEROS (95.3%) |
| 15 | `EndurecedorMiolo` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 16 | `RotacaoMaxima` | MUITOS NULOS (96.0%) | VALOR ÚNICO (500.0) |
| 17 | `CustoMetro` | MUITOS ZEROS (93.8%) |
| 18 | `CustoMetroQuad` | MUITOS ZEROS (93.8%) |
| 19 | `FormatoPadrao` | MUITOS NULOS (96.0%) | VALOR ÚNICO (2200) |
| 20 | `LogGantt` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 21 | `CompMinConj` | MUITOS ZEROS (96.0%) |
| 22 | `ProdutividadePadrao` | MUITOS ZEROS (94.0%) |
| 23 | `EficienciaPadrao` | MUITOS ZEROS (94.0%) |
| 24 | `FimPrevParadaAtual` | MUITOS NULOS (94.0%) |
| 25 | `IDSecaoMaquinaParadaAtual` | MUITOS NULOS (100.0%) |
| 26 | `Desativada` | MUITOS ZEROS (82.0%) |
| 27 | `PerdaLimiteAviso` | MUITOS ZEROS (96.0%) |
| 28 | `UnidadeApontConjugacao` | VALOR ÚNICO (1) |
| 29 | `TestePorBoletim` | VALOR ÚNICO (1) |
| 30 | `idJornada` | VALOR ÚNICO (1.0) |
| 31 | `DistMinVincos` | MUITOS ZEROS (98.0%) |
| 32 | `IDCentroCusto` | MUITOS NULOS (100.0%) |
| 33 | `IDCentroCustoMaq` | MUITOS NULOS (100.0%) |
| 34 | `idSessaoDB` | MUITOS NULOS (100.0%) |
| 35 | `ValidaInterseccaoApontamento` | VALOR ÚNICO (3) |
| 36 | `DescValidaInterseccaoApontamento` | VALOR ÚNICO (Não será efetuada validação para esta máquina) |
| 37 | `ValidaBuracoApontamento` | VALOR ÚNICO (2) |
| 38 | `DescValidaBuracoApontamento` | VALOR ÚNICO (Não será efetuada validação para esta máquina) |
| 39 | `ConsegueRefilarSomenteUmLado` | VALOR ÚNICO (1) |
| 40 | `idUnidadeFabril` | VALOR ÚNICO (1.0) |
| 41 | `AreaM2PerdidaPorConjugacao` | VALOR ÚNICO (10) |
| 42 | `AreaM2PerdidoTrocaFormato` | MUITOS ZEROS (98.0%) |
| 43 | `PedidoMinimoKG` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 44 | `LimitaMinimoAcessorio` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| 45 | `DisponivelLoteNovo` | VALOR ÚNICO (True) |
| 46 | `PerdaProducaoPerc` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 47 | `PerdaProducaoPecas` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 48 | `DeslocamentoMaximPortaBobinas_mm` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 49 | `LarguraLimiteEstabilidadePilhaChapas` | VALOR ÚNICO (600) |
| 50 | `ComprimentoRefugoGuilhotina` | MUITOS NULOS (100.0%) |
| 51 | `HabilitarIntegracaoEsteiraOnduladeira` | MUITOS ZEROS (96.0%) |
| 52 | `TamanhoLimiteEstradoConsideraCombinacaoEstrados` | VALOR ÚNICO (True) |
| 53 | `TamanhoLimiteEstradoAlinhadoOrientacaoEsteira` | VALOR ÚNICO (2000) |
| 54 | `TamanhoLimiteEstradoTransversalOrientacaoEsteira` | VALOR ÚNICO (2000) |

---

## Análise Detalhada de Todas as Colunas

| Coluna | Ação | Nulos (%) | Valores Únicos | Variância (%) | Zeros (%) | Vazias (%) | Tipo | Motivos |
|--------|------|-----------|----------------|---------------|-----------|------------|------|---------|
| `MAQ_Id` | <span class='manter'>MANTER</span> | 0.0% | 50 | 100.0% | 0.0% | 0% | `int64` | OK |
| `Maquina` | <span class='manter'>MANTER</span> | 0.0% | 50 | 100.0% | 0% | 0.0% | `object` | OK |
| `NomeMaquina` | <span class='manter'>MANTER</span> | 0.0% | 49 | 98.0% | 0% | 0.0% | `object` | OK |
| `Tipo` | <span class='manter'>MANTER</span> | 0.0% | 9 | 18.0% | 4.0% | 0% | `int64` | OK |
| `Facoes` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 4.0% | 96.0% | 0% | `int64` | MUITOS ZEROS (96.0%) |
| `LargUtilMax` | <span class='excluir'>EXCLUIR</span> | 0.0% | 3 | 6.0% | 96.0% | 0% | `int64` | MUITOS ZEROS (96.0%) |
| `LargMinChapa` | <span class='excluir'>EXCLUIR</span> | 0.0% | 3 | 6.0% | 96.0% | 0% | `int64` | MUITOS ZEROS (96.0%) |
| `LargMaxChapa` | <span class='excluir'>EXCLUIR</span> | 0.0% | 3 | 6.0% | 96.0% | 0% | `int64` | MUITOS ZEROS (96.0%) |
| `CompMinChapa` | <span class='excluir'>EXCLUIR</span> | 96.0% | 1 | 50.0% | 0.0% | 0% | `float64` | MUITOS NULOS (96.0%) | VALOR ÚNICO (620.0) |
| `CompMaxChapa` | <span class='excluir'>EXCLUIR</span> | 96.0% | 1 | 50.0% | 0.0% | 0% | `float64` | MUITOS NULOS (96.0%) | VALOR ÚNICO (4000.0) |
| `RefiloMin` | <span class='excluir'>EXCLUIR</span> | 96.0% | 2 | 100.0% | 0.0% | 0% | `float64` | MUITOS NULOS (96.0%) |
| `RefiloMax` | <span class='excluir'>EXCLUIR</span> | 96.0% | 1 | 50.0% | 0.0% | 0% | `float64` | MUITOS NULOS (96.0%) | VALOR ÚNICO (176.0) |
| `Facas` | <span class='excluir'>EXCLUIR</span> | 96.0% | 1 | 50.0% | 0.0% | 0% | `float64` | MUITOS NULOS (96.0%) | VALOR ÚNICO (7.0) |
| `PermiteMisturarFerramentas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 4.0% | 96.0% | 0% | `bool` | MUITOS ZEROS (96.0%) |
| `idTipoVincoPadrao` | <span class='excluir'>EXCLUIR</span> | 96.0% | 1 | 50.0% | 0.0% | 0% | `float64` | MUITOS NULOS (96.0%) | VALOR ÚNICO (16.0) |
| `TearTape` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `ResinaInterna` | <span class='excluir'>EXCLUIR</span> | 14.0% | 2 | 4.7% | 95.3% | 0% | `float64` | MUITOS ZEROS (95.3%) |
| `ResinaExterna` | <span class='excluir'>EXCLUIR</span> | 14.0% | 2 | 4.7% | 95.3% | 0% | `float64` | MUITOS ZEROS (95.3%) |
| `EndurecedorMiolo` | <span class='excluir'>EXCLUIR</span> | 14.0% | 1 | 2.3% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `RotacaoMaxima` | <span class='excluir'>EXCLUIR</span> | 96.0% | 1 | 50.0% | 0.0% | 0% | `float64` | MUITOS NULOS (96.0%) | VALOR ÚNICO (500.0) |
| `CustoHora` | <span class='manter'>MANTER</span> | 24.0% | 18 | 47.4% | 7.9% | 0% | `float64` | OK |
| `CustoMetro` | <span class='excluir'>EXCLUIR</span> | 36.0% | 2 | 6.2% | 93.8% | 0% | `float64` | MUITOS ZEROS (93.8%) |
| `CustoMetroQuad` | <span class='excluir'>EXCLUIR</span> | 36.0% | 2 | 6.2% | 93.8% | 0% | `float64` | MUITOS ZEROS (93.8%) |
| `FormatoPadrao` | <span class='excluir'>EXCLUIR</span> | 96.0% | 1 | 50.0% | 0% | 0.0% | `object` | MUITOS NULOS (96.0%) | VALOR ÚNICO (2200) |
| `UnidProdutividade` | <span class='manter'>MANTER</span> | 0.0% | 3 | 6.0% | 48.0% | 0% | `int64` | OK |
| `DescUnidProdutividade` | <span class='manter'>MANTER</span> | 0.0% | 3 | 6.0% | 0% | 0.0% | `object` | OK |
| `Setup` | <span class='manter'>MANTER</span> | 0.0% | 9 | 18.0% | 18.0% | 0% | `int64` | OK |
| `ProdM2` | <span class='manter'>MANTER</span> | 0.0% | 28 | 56.0% | 14.0% | 0% | `int64` | OK |
| `ProdBatidas` | <span class='manter'>MANTER</span> | 0.0% | 28 | 56.0% | 8.0% | 0% | `int64` | OK |
| `ProdKg` | <span class='manter'>MANTER</span> | 0.0% | 20 | 40.0% | 20.0% | 0% | `int64` | OK |
| `ProdMaquina` | <span class='manter'>MANTER</span> | 0.0% | 30 | 60.0% | 0.0% | 0% | `int64` | OK |
| `HomensTurma` | <span class='manter'>MANTER</span> | 32.0% | 8 | 23.5% | 0.0% | 0% | `float64` | OK |
| `Gantt` | <span class='manter'>MANTER</span> | 0.0% | 2 | 4.0% | 74.0% | 0% | `int64` | OK |
| `NrDeCores` | <span class='manter'>MANTER</span> | 64.0% | 4 | 22.2% | 22.2% | 0% | `float64` | OK |
| `LogGantt` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `CompMinConj` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 4.0% | 96.0% | 0% | `int64` | MUITOS ZEROS (96.0%) |
| `IDGrupoMaquina` | <span class='manter'>MANTER</span> | 32.0% | 15 | 44.1% | 0.0% | 0% | `float64` | OK |
| `ProdutividadePadrao` | <span class='excluir'>EXCLUIR</span> | 0.0% | 4 | 8.0% | 94.0% | 0% | `int64` | MUITOS ZEROS (94.0%) |
| `EficienciaPadrao` | <span class='excluir'>EXCLUIR</span> | 0.0% | 4 | 8.0% | 94.0% | 0% | `int64` | MUITOS ZEROS (94.0%) |
| `TarefaAtual` | <span class='manter'>MANTER</span> | 80.0% | 10 | 100.0% | 0% | 0.0% | `object` | OK |
| `InicioTarefaAtual` | <span class='manter'>MANTER</span> | 34.0% | 32 | 97.0% | 0% | 0% | `datetime64[ns]` | OK |
| `FimPrevTarefaAtual` | <span class='manter'>MANTER</span> | 34.0% | 33 | 100.0% | 0% | 0% | `datetime64[ns]` | OK |
| `ParadaAtual` | <span class='manter'>MANTER</span> | 88.0% | 6 | 100.0% | 0.0% | 0% | `float64` | OK |
| `InicioParadaAtual` | <span class='manter'>MANTER</span> | 28.0% | 35 | 97.2% | 0% | 0% | `datetime64[ns]` | OK |
| `FimPrevParadaAtual` | <span class='excluir'>EXCLUIR</span> | 94.0% | 3 | 100.0% | 0% | 0% | `datetime64[ns]` | MUITOS NULOS (94.0%) |
| `IDSecaoMaquinaParadaAtual` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ProgramarProducao` | <span class='manter'>MANTER</span> | 0.0% | 2 | 4.0% | 16.0% | 0% | `bool` | OK |
| `Desativada` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 4.0% | 82.0% | 0% | `int64` | MUITOS ZEROS (82.0%) |
| `CodigoERP` | <span class='manter'>MANTER</span> | 16.0% | 40 | 95.2% | 0% | 4.8% | `object` | OK |
| `PerdaLimiteAviso` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 4.0% | 96.0% | 0% | `int64` | MUITOS ZEROS (96.0%) |
| `UnidadeApontConjugacao` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (1) |
| `TestePorBoletim` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (1) |
| `idJornada` | <span class='excluir'>EXCLUIR</span> | 14.0% | 1 | 2.3% | 0.0% | 0% | `float64` | VALOR ÚNICO (1.0) |
| `DistMinVincos` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 4.0% | 98.0% | 0% | `int64` | MUITOS ZEROS (98.0%) |
| `IDCentroCusto` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `IDCentroCustoMaq` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `idSessaoDB` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PorcMinLarguraResinada` | <span class='manter'>MANTER</span> | 0.0% | 3 | 6.0% | 2.0% | 0% | `int64` | OK |
| `CargaMaqLote` | <span class='manter'>MANTER</span> | 0.0% | 2 | 4.0% | 32.0% | 0% | `int64` | OK |
| `ValidaInterseccaoApontamento` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (3) |
| `DescValidaInterseccaoApontamento` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0% | 0.0% | `object` | VALOR ÚNICO (Não será efetuada validação para esta máquina) |
| `ValidaBuracoApontamento` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (2) |
| `DescValidaBuracoApontamento` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0% | 0.0% | `object` | VALOR ÚNICO (Não será efetuada validação para esta máquina) |
| `ConsegueRefilarSomenteUmLado` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (1) |
| `idUnidadeFabril` | <span class='excluir'>EXCLUIR</span> | 70.0% | 1 | 6.7% | 0.0% | 0% | `float64` | VALOR ÚNICO (1.0) |
| `RefileDiretoPrensa` | <span class='manter'>MANTER</span> | 0.0% | 2 | 4.0% | 8.0% | 0% | `bool` | OK |
| `AreaM2PerdidaPorConjugacao` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (10) |
| `AreaM2PerdidoTrocaFormato` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 4.0% | 98.0% | 0% | `int64` | MUITOS ZEROS (98.0%) |
| `DifPorcProdutividadeMaqFT_Menos` | <span class='manter'>MANTER</span> | 0.0% | 3 | 6.0% | 2.0% | 0% | `int64` | OK |
| `DifPorcProdutividadeMaqFT_Mais` | <span class='manter'>MANTER</span> | 0.0% | 3 | 6.0% | 2.0% | 0% | `int64` | OK |
| `PedidoMinimoM2` | <span class='manter'>MANTER</span> | 0.0% | 3 | 6.0% | 66.0% | 0% | `int64` | OK |
| `PedidoMinimoKG` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `LimitaMinimoAcessorio` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| `DisponivelLoteNovo` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0.0% | 0% | `bool` | VALOR ÚNICO (True) |
| `PerdaProducaoPerc` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `PerdaProducaoPecas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `DeslocamentoMaximPortaBobinas_mm` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `LarguraLimiteEstabilidadePilhaChapas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (600) |
| `ComprimentoRefugoGuilhotina` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `HabilitarIntegracaoEsteiraOnduladeira` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 4.0% | 96.0% | 0% | `bool` | MUITOS ZEROS (96.0%) |
| `TamanhoLimiteEstradoConsideraCombinacaoEstrados` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0.0% | 0% | `bool` | VALOR ÚNICO (True) |
| `TamanhoLimiteEstradoAlinhadoOrientacaoEsteira` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (2000) |
| `TamanhoLimiteEstradoTransversalOrientacaoEsteira` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 2.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (2000) |

---

## Critérios de Exclusão Utilizados

- Muitos Nulos: > 90% de valores nulos
- Valor Único: coluna possui apenas 1 valor único
- Muitos Zeros: > 80% de valores zero (para colunas numéricas)
- Strings Vazias: > 80% de strings vazias (para colunas de texto)

Colunas que não atendem a esses critérios são mantidas.
