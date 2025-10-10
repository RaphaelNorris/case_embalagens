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
- **Tabela:** `dbo.Itens`
- **Data/Hora:** 2025-09-24 13:35:31
- **Total de Registros:** 10699
- **Total de Colunas:** 220
- **Autor:** Raphael Norris

---

## Filtros Aplicados
- **DataCriacao** >= `2022-01-01`

---

## Query Executada
```sql
SELECT * FROM dbo.Itens WHERE DataCriacao >= `2022-01-01`
```



---

## Resumo da Análise

| Métrica | Valor |
|---------|-------|
| Total de Colunas | 220 |
| Colunas para Manter | 121 |
| Colunas para Excluir | 99 |
| Percentual de Exclusão | 45.0% |

---

## Colunas Sugeridas para Exclusão

| # | Coluna | Motivos |
|---|--------|---------|
| 1 | `idTipoFT` | MUITOS NULOS (99.3%) | VALOR ÚNICO (1.0) |
| 2 | `idTipoFT2` | MUITOS NULOS (99.5%) | VALOR ÚNICO (2.0) |
| 3 | `idTipoFT3` | MUITOS NULOS (100.0%) | VALOR ÚNICO (4.0) |
| 4 | `idTipoFT4` | MUITOS NULOS (100.0%) |
| 5 | `idTipoFT5` | MUITOS NULOS (100.0%) |
| 6 | `IDAgrupamento` | MUITOS NULOS (99.7%) | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 7 | `RazaoSusp` | MUITOS NULOS (100.0%) |
| 8 | `CodigoEAN` | MUITOS NULOS (99.8%) | VALOR ÚNICO (1) |
| 9 | `CrushMinimo` | MUITOS NULOS (92.3%) |
| 10 | `CobbInt30Maximo` | MUITOS NULOS (99.8%) |
| 11 | `CobbExt30Maximo` | MUITOS NULOS (99.9%) |
| 12 | `TesteFisicoAdicional1` | MUITOS NULOS (100.0%) |
| 13 | `PAT_Interno` | MUITOS NULOS (100.0%) |
| 14 | `PAT_Externo` | MUITOS NULOS (100.0%) |
| 15 | `Umidade` | MUITOS NULOS (100.0%) | VALOR ÚNICO (9.0) |
| 16 | `Compressao` | MUITOS NULOS (97.4%) |
| 17 | `ProfundidadeVinco` | MUITOS NULOS (100.0%) |
| 18 | `ForcaDeVinco1` | MUITOS NULOS (100.0%) |
| 19 | `ForcaDeVinco2` | MUITOS NULOS (100.0%) |
| 20 | `ForcaDeVinco3` | MUITOS NULOS (100.0%) |
| 21 | `FormatoSimplex` | MUITOS NULOS (99.9%) | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 22 | `VincosLargNoRiscador` | MUITOS ZEROS (98.0%) |
| 23 | `VincoLarg4` | MUITOS NULOS (99.4%) |
| 24 | `VincoLarg5` | MUITOS NULOS (99.8%) |
| 25 | `VincoLarg6` | MUITOS NULOS (99.9%) |
| 26 | `VincoLarg7` | MUITOS NULOS (100.0%) |
| 27 | `VincoLarg8` | MUITOS NULOS (100.0%) |
| 28 | `VincoLarg9` | MUITOS NULOS (100.0%) |
| 29 | `VincoLarg10` | MUITOS NULOS (100.0%) |
| 30 | `VincosCompNoRiscador` | MUITOS ZEROS (97.7%) |
| 31 | `VincoComp6` | MUITOS NULOS (100.0%) |
| 32 | `VincoComp7` | MUITOS NULOS (100.0%) |
| 33 | `VincoComp8` | MUITOS NULOS (100.0%) |
| 34 | `VincoComp9` | MUITOS NULOS (100.0%) |
| 35 | `VincoComp10` | MUITOS NULOS (100.0%) |
| 36 | `TearTape1` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 37 | `TearTape2` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 38 | `TearTape3` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 39 | `TearTape4` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 40 | `ProlongLap` | MUITOS ZEROS (93.5%) |
| 41 | `Rejeito` | MUITOS ZEROS (96.9%) |
| 42 | `RejeitoPecas` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 43 | `ResinaInterna` | MUITOS ZEROS (87.3%) |
| 44 | `ResinaInternaSN` | MUITOS ZEROS (87.3%) |
| 45 | `ResinaExterna` | MUITOS ZEROS (100.0%) |
| 46 | `ResinaExternaSN` | MUITOS ZEROS (100.0%) |
| 47 | `EndurecedorMiolo` | MUITOS NULOS (99.2%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| 48 | `EndurecedorMioloSN` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 49 | `Grampos` | MUITOS ZEROS (96.9%) |
| 50 | `FitilhosCompPacote` | MUITOS ZEROS (97.6%) |
| 51 | `FacesOpostas` | MUITOS ZEROS (98.7%) |
| 52 | `Cantoneiras` | MUITOS ZEROS (93.9%) |
| 53 | `OrelhasInvertidas` | MUITOS ZEROS (98.2%) |
| 54 | `ConsumoCor1` | MUITOS NULOS (92.1%) |
| 55 | `ViscosidadeCor1` | MUITOS NULOS (100.0%) |
| 56 | `ViscosidadeCor2` | MUITOS NULOS (100.0%) | VALOR ÚNICO (910.0) |
| 57 | `ViscosidadeCor3` | MUITOS NULOS (100.0%) |
| 58 | `ViscosidadeCor4` | MUITOS NULOS (100.0%) |
| 59 | `Cor5` | MUITOS NULOS (91.5%) | STRINGS VAZIAS (99.8%) |
| 60 | `ConsumoCor5` | MUITOS NULOS (100.0%) |
| 61 | `ViscosidadeCor5` | MUITOS NULOS (100.0%) |
| 62 | `Cor6` | MUITOS NULOS (91.8%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| 63 | `ConsumoCor6` | MUITOS NULOS (100.0%) |
| 64 | `ViscosidadeCor6` | MUITOS NULOS (100.0%) |
| 65 | `ImpComRegistro` | MUITOS ZEROS (82.6%) |
| 66 | `DetalheCV` | MUITOS ZEROS (85.0%) |
| 67 | `Obs5` | STRINGS VAZIAS (84.8%) |
| 68 | `TipoObs6` | MUITOS NULOS (93.0%) |
| 69 | `Obs6` | STRINGS VAZIAS (89.6%) |
| 70 | `TipoObs7` | MUITOS NULOS (94.6%) |
| 71 | `Obs7` | STRINGS VAZIAS (91.6%) |
| 72 | `TipoObs8` | MUITOS NULOS (94.5%) |
| 73 | `Obs8` | STRINGS VAZIAS (90.9%) |
| 74 | `DimAdic3` | MUITOS NULOS (97.6%) |
| 75 | `DimAdic4` | MUITOS NULOS (98.3%) |
| 76 | `DimAdic5` | MUITOS NULOS (98.2%) |
| 77 | `DimAdic6` | MUITOS NULOS (98.2%) |
| 78 | `ContraOnda` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| 79 | `ComissaoDeVendas` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 80 | `PesoAdic` | MUITOS NULOS (93.9%) | MUITOS ZEROS (96.6%) |
| 81 | `CustoUnitAdic` | MUITOS NULOS (99.9%) | VALOR ÚNICO (35.0) |
| 82 | `PorosidadeMinimo` | MUITOS NULOS (100.0%) |
| 83 | `RefiloOnduladeira` | MUITOS NULOS (100.0%) |
| 84 | `TipoCustoExtra` | MUITOS NULOS (100.0%) |
| 85 | `TravaComposicao` | MUITOS ZEROS (86.1%) |
| 86 | `PrecoNegociado` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 87 | `RefiloOndOrcam` | MUITOS NULOS (100.0%) |
| 88 | `RefiloCompOrcam` | MUITOS NULOS (100.0%) |
| 89 | `GrupoPaletizacao` | MUITOS NULOS (100.0%) |
| 90 | `PathFiguraDaFT` | STRINGS VAZIAS (95.0%) |
| 91 | `PressaoDeArqueamento` | MUITOS NULOS (99.3%) | MUITOS ZEROS (96.1%) |
| 92 | `ReferenciaGrupoPaletizacao` | MUITOS NULOS (100.0%) |
| 93 | `CodigoERP` | MUITOS NULOS (100.0%) |
| 94 | `FlagEstoqueOuTerceiros` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 95 | `DescFlagEstoqueOuTerceiros` | VALOR ÚNICO (0-normal) |
| 96 | `AreaUtilCedidaFaca` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 97 | `idUsuarioAnalise` | MUITOS NULOS (100.0%) |
| 98 | `PrecoFerramentas` | MUITOS NULOS (100.0%) |
| 99 | `QuantPrevista` | VALOR ÚNICO (1) |

---

## Análise Detalhada de Todas as Colunas

| Coluna | Ação | Nulos (%) | Valores Únicos | Variância (%) | Zeros (%) | Vazias (%) | Tipo | Motivos |
|--------|------|-----------|----------------|---------------|-----------|------------|------|---------|
| `Item` | <span class='manter'>MANTER</span> | 0.0% | 10699 | 100.0% | 0% | 0.0% | `object` | OK |
| `Conjunto` | <span class='manter'>MANTER</span> | 0.0% | 9685 | 90.5% | 0% | 0.0% | `object` | OK |
| `idTipoFT` | <span class='excluir'>EXCLUIR</span> | 99.3% | 1 | 1.4% | 0.0% | 0% | `float64` | MUITOS NULOS (99.3%) | VALOR ÚNICO (1.0) |
| `idTipoFT2` | <span class='excluir'>EXCLUIR</span> | 99.5% | 1 | 1.7% | 0.0% | 0% | `float64` | MUITOS NULOS (99.5%) | VALOR ÚNICO (2.0) |
| `idTipoFT3` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 20.0% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) | VALOR ÚNICO (4.0) |
| `idTipoFT4` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `idTipoFT5` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `IDTipoIPI` | <span class='manter'>MANTER</span> | 0.2% | 3 | 0.0% | 0.0% | 0% | `float64` | OK |
| `IDClassFiscal` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 0.0% | 0% | `float64` | OK |
| `IDFamilia` | <span class='manter'>MANTER</span> | 1.1% | 71 | 0.7% | 3.2% | 0% | `float64` | OK |
| `IDAgrupamento` | <span class='excluir'>EXCLUIR</span> | 99.7% | 1 | 3.2% | 100.0% | 0% | `float64` | MUITOS NULOS (99.7%) | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `EstadoFT_Detec` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 31.4% | 0% | `int64` | OK |
| `TextoEstadoFT_Detec` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 0% | 0.0% | `object` | OK |
| `RazaoEstadoFT` | <span class='manter'>MANTER</span> | 0.0% | 766 | 7.2% | 0% | 22.0% | `object` | OK |
| `StatusFT` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 2.9% | 0% | `int64` | OK |
| `TextoStatusFT` | <span class='manter'>MANTER</span> | 0.0% | 40 | 0.4% | 0% | 0.0% | `object` | OK |
| `RazaoSusp` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Versao` | <span class='manter'>MANTER</span> | 0.0% | 38 | 0.4% | 0.0% | 0% | `int64` | OK |
| `ObsVersao` | <span class='manter'>MANTER</span> | 0.0% | 7100 | 66.4% | 0% | 0.0% | `object` | OK |
| `IDCliente` | <span class='manter'>MANTER</span> | 0.0% | 1319 | 12.3% | 0.0% | 0% | `int64` | OK |
| `Referencia` | <span class='manter'>MANTER</span> | 0.0% | 9742 | 91.1% | 0% | 0.0% | `object` | OK |
| `CodigoReferencia` | <span class='manter'>MANTER</span> | 28.7% | 2885 | 37.8% | 0% | 46.1% | `object` | OK |
| `CodigoEAN` | <span class='excluir'>EXCLUIR</span> | 99.8% | 1 | 4.2% | 0% | 0.0% | `object` | MUITOS NULOS (99.8%) | VALOR ÚNICO (1) |
| `TipoABNT` | <span class='manter'>MANTER</span> | 0.0% | 99 | 0.9% | 0% | 0.0% | `object` | OK |
| `PecasPorUnidade` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 0.0% | 0% | `float64` | OK |
| `UnidadesPorConjunto` | <span class='manter'>MANTER</span> | 0.0% | 7 | 0.1% | 0.0% | 0% | `float64` | OK |
| `PecasPorConjunto` | <span class='manter'>MANTER</span> | 0.0% | 7 | 0.1% | 0.0% | 0% | `float64` | OK |
| `ExigeLaudo` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 18.8% | 0% | `int64` | OK |
| `Gramatura` | <span class='manter'>MANTER</span> | 21.3% | 175 | 2.1% | 0.0% | 0% | `float64` | OK |
| `MullenMinimo` | <span class='manter'>MANTER</span> | 31.9% | 43 | 0.6% | 0.0% | 0% | `float64` | OK |
| `CrushMinimo` | <span class='excluir'>EXCLUIR</span> | 92.3% | 24 | 2.9% | 0.0% | 0% | `float64` | MUITOS NULOS (92.3%) |
| `ColunaMinimo` | <span class='manter'>MANTER</span> | 8.7% | 66 | 0.7% | 0.0% | 0% | `float64` | OK |
| `CobbIntMaximo` | <span class='manter'>MANTER</span> | 27.3% | 15 | 0.2% | 0.0% | 0% | `float64` | OK |
| `CobbExtMaximo` | <span class='manter'>MANTER</span> | 27.4% | 13 | 0.2% | 0.0% | 0% | `float64` | OK |
| `CobbInt30Maximo` | <span class='excluir'>EXCLUIR</span> | 99.8% | 5 | 22.7% | 0.0% | 0% | `float64` | MUITOS NULOS (99.8%) |
| `CobbExt30Maximo` | <span class='excluir'>EXCLUIR</span> | 99.9% | 3 | 50.0% | 0.0% | 0% | `float64` | MUITOS NULOS (99.9%) |
| `TesteFisicoAdicional1` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PAT_Interno` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PAT_Externo` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Espessura` | <span class='manter'>MANTER</span> | 20.8% | 50 | 0.6% | 0.0% | 0% | `float64` | OK |
| `Umidade` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 100.0% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) | VALOR ÚNICO (9.0) |
| `Compressao` | <span class='excluir'>EXCLUIR</span> | 97.4% | 99 | 35.2% | 0.0% | 0% | `float64` | MUITOS NULOS (97.4%) |
| `ProfundidadeVinco` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ForcaDeVinco1` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ForcaDeVinco2` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ForcaDeVinco3` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Composicao` | <span class='manter'>MANTER</span> | 0.0% | 60 | 0.6% | 0% | 0.0% | `object` | OK |
| `FormatoSimplex` | <span class='excluir'>EXCLUIR</span> | 99.9% | 1 | 16.7% | 100.0% | 0% | `float64` | MUITOS NULOS (99.9%) | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `Largura` | <span class='manter'>MANTER</span> | 0.0% | 1127 | 10.5% | 0.0% | 0% | `int64` | OK |
| `RefiloLargura` | <span class='manter'>MANTER</span> | 0.0% | 21 | 0.2% | 62.2% | 0% | `int64` | OK |
| `Comprimento` | <span class='manter'>MANTER</span> | 0.0% | 1798 | 16.8% | 0.0% | 0% | `int64` | OK |
| `RefiloComprimento` | <span class='manter'>MANTER</span> | 0.0% | 17 | 0.2% | 57.9% | 0% | `int64` | OK |
| `MultLarg` | <span class='manter'>MANTER</span> | 0.0% | 7 | 0.1% | 0.0% | 0% | `int64` | OK |
| `MultComp` | <span class='manter'>MANTER</span> | 0.0% | 8 | 0.1% | 0.0% | 0% | `int64` | OK |
| `Arranjo` | <span class='manter'>MANTER</span> | 0.0% | 17 | 0.2% | 0.0% | 0% | `int64` | OK |
| `RefugoCliente` | <span class='manter'>MANTER</span> | 0.0% | 5461 | 51.0% | 5.2% | 0% | `float64` | OK |
| `VincosLargNoRiscador` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 98.0% | 0% | `bool` | MUITOS ZEROS (98.0%) |
| `VincoLarg1` | <span class='manter'>MANTER</span> | 41.6% | 237 | 3.8% | 0.0% | 0% | `float64` | OK |
| `VincoLarg2` | <span class='manter'>MANTER</span> | 41.6% | 532 | 8.5% | 0.0% | 0% | `float64` | OK |
| `VincoLarg3` | <span class='manter'>MANTER</span> | 45.2% | 216 | 3.7% | 0.0% | 0% | `float64` | OK |
| `VincoLarg4` | <span class='excluir'>EXCLUIR</span> | 99.4% | 37 | 56.1% | 0.0% | 0% | `float64` | MUITOS NULOS (99.4%) |
| `VincoLarg5` | <span class='excluir'>EXCLUIR</span> | 99.8% | 14 | 63.6% | 0.0% | 0% | `float64` | MUITOS NULOS (99.8%) |
| `VincoLarg6` | <span class='excluir'>EXCLUIR</span> | 99.9% | 6 | 75.0% | 0.0% | 0% | `float64` | MUITOS NULOS (99.9%) |
| `VincoLarg7` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `VincoLarg8` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `VincoLarg9` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `VincoLarg10` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `VincosCompNoRiscador` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 97.7% | 0% | `bool` | MUITOS ZEROS (97.7%) |
| `VincoComp1` | <span class='manter'>MANTER</span> | 41.2% | 58 | 0.9% | 0.0% | 0% | `float64` | OK |
| `VincoComp2` | <span class='manter'>MANTER</span> | 41.4% | 402 | 6.4% | 0.0% | 0% | `float64` | OK |
| `VincoComp3` | <span class='manter'>MANTER</span> | 41.7% | 517 | 8.3% | 0.0% | 0% | `float64` | OK |
| `VincoComp4` | <span class='manter'>MANTER</span> | 42.3% | 380 | 6.2% | 0.0% | 0% | `float64` | OK |
| `VincoComp5` | <span class='manter'>MANTER</span> | 42.4% | 492 | 8.0% | 0.0% | 0% | `float64` | OK |
| `VincoComp6` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `VincoComp7` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `VincoComp8` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `VincoComp9` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `VincoComp10` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `TearTape1` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `TearTape2` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `TearTape3` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `TearTape4` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `Lap` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 42.2% | 0% | `int64` | OK |
| `ProlongLap` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 93.5% | 0% | `int64` | MUITOS ZEROS (93.5%) |
| `LapNoComp` | <span class='manter'>MANTER</span> | 0.0% | 3 | 0.0% | 55.9% | 0% | `int64` | OK |
| `TextoLapNoComp` | <span class='manter'>MANTER</span> | 0.0% | 3 | 0.0% | 0% | 0.0% | `object` | OK |
| `LapInterno` | <span class='manter'>MANTER</span> | 0.0% | 3 | 0.0% | 0.1% | 0% | `int64` | OK |
| `TextoLapInterno` | <span class='manter'>MANTER</span> | 0.0% | 3 | 0.0% | 0% | 0.0% | `object` | OK |
| `LapPrimVinco` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 42.4% | 0% | `int64` | OK |
| `Refilado` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 0.2% | 0% | `int64` | OK |
| `Rejeito` | <span class='excluir'>EXCLUIR</span> | 0.0% | 4 | 0.0% | 96.9% | 0% | `int64` | MUITOS ZEROS (96.9%) |
| `RejeitoPecas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `ResinaInterna` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 87.3% | 0% | `int64` | MUITOS ZEROS (87.3%) |
| `ResinaInternaSN` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 87.3% | 0% | `int64` | MUITOS ZEROS (87.3%) |
| `ResinaExterna` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 100.0% | 0% | `int64` | MUITOS ZEROS (100.0%) |
| `ResinaExternaSN` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 100.0% | 0% | `int64` | MUITOS ZEROS (100.0%) |
| `EndurecedorMiolo` | <span class='excluir'>EXCLUIR</span> | 99.2% | 1 | 1.1% | 0% | 100.0% | `object` | MUITOS NULOS (99.2%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| `EndurecedorMioloSN` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `Fechamento` | <span class='manter'>MANTER</span> | 2.4% | 15 | 0.1% | 0% | 0.0% | `object` | OK |
| `Grampos` | <span class='excluir'>EXCLUIR</span> | 81.1% | 20 | 1.0% | 96.9% | 0% | `float64` | MUITOS ZEROS (96.9%) |
| `Amarrado` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 9.9% | 0% | `int64` | OK |
| `FitilhosLargPacote` | <span class='manter'>MANTER</span> | 1.1% | 3 | 0.0% | 10.7% | 0% | `float64` | OK |
| `FitilhosCompPacote` | <span class='excluir'>EXCLUIR</span> | 7.7% | 3 | 0.0% | 97.6% | 0% | `float64` | MUITOS ZEROS (97.6%) |
| `Paletizado` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 4.4% | 0% | `int64` | OK |
| `PacotesLargura` | <span class='manter'>MANTER</span> | 14.0% | 13 | 0.1% | 0.3% | 0% | `float64` | OK |
| `PacotesComprimento` | <span class='manter'>MANTER</span> | 13.2% | 14 | 0.2% | 0.3% | 0% | `float64` | OK |
| `PacotesAltura` | <span class='manter'>MANTER</span> | 2.7% | 32 | 0.3% | 0.0% | 0% | `float64` | OK |
| `PecasPorPacote` | <span class='manter'>MANTER</span> | 0.0% | 27 | 0.3% | 0.4% | 0% | `int64` | OK |
| `PecasPorPalete` | <span class='manter'>MANTER</span> | 15.0% | 162 | 1.8% | 0.6% | 0% | `float64` | OK |
| `PacotesPorPalete` | <span class='manter'>MANTER</span> | 15.0% | 98 | 1.1% | 0.3% | 0% | `float64` | OK |
| `UnidadesPorPalete` | <span class='manter'>MANTER</span> | 15.0% | 160 | 1.8% | 0.6% | 0% | `float64` | OK |
| `FitasLargPalete` | <span class='manter'>MANTER</span> | 3.9% | 3 | 0.0% | 1.1% | 0% | `float64` | OK |
| `FitasCompPalete` | <span class='manter'>MANTER</span> | 3.9% | 4 | 0.0% | 1.2% | 0% | `float64` | OK |
| `FacesOpostas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 98.7% | 0% | `int64` | MUITOS ZEROS (98.7%) |
| `Espelho` | <span class='manter'>MANTER</span> | 0.0% | 4 | 0.0% | 7.1% | 0% | `int64` | OK |
| `Cantoneiras` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 93.9% | 0% | `int64` | MUITOS ZEROS (93.9%) |
| `Filme` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 6.8% | 0% | `int64` | OK |
| `OrelhasInvertidas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 98.2% | 0% | `int64` | MUITOS ZEROS (98.2%) |
| `Faca` | <span class='manter'>MANTER</span> | 51.8% | 1594 | 30.9% | 0% | 0.0% | `object` | OK |
| `CodFI` | <span class='manter'>MANTER</span> | 50.1% | 3073 | 57.5% | 0% | 0.0% | `object` | OK |
| `Cor1` | <span class='manter'>MANTER</span> | 53.3% | 64 | 1.3% | 0% | 77.6% | `object` | OK |
| `ConsumoCor1` | <span class='excluir'>EXCLUIR</span> | 92.1% | 440 | 52.3% | 0.0% | 0% | `float64` | MUITOS NULOS (92.1%) |
| `ViscosidadeCor1` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Cor2` | <span class='manter'>MANTER</span> | 57.8% | 95 | 2.1% | 0% | 61.2% | `object` | OK |
| `ConsumoCor2` | <span class='manter'>MANTER</span> | 86.5% | 799 | 55.3% | 0.1% | 0% | `float64` | OK |
| `ViscosidadeCor2` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 100.0% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) | VALOR ÚNICO (910.0) |
| `Cor3` | <span class='manter'>MANTER</span> | 61.7% | 82 | 2.0% | 0% | 49.2% | `object` | OK |
| `ConsumoCor3` | <span class='manter'>MANTER</span> | 84.0% | 871 | 51.0% | 0.1% | 0% | `float64` | OK |
| `ViscosidadeCor3` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Cor4` | <span class='manter'>MANTER</span> | 59.1% | 32 | 0.7% | 0% | 32.3% | `object` | OK |
| `ConsumoCor4` | <span class='manter'>MANTER</span> | 77.7% | 961 | 40.2% | 0.1% | 0% | `float64` | OK |
| `ViscosidadeCor4` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Cor5` | <span class='excluir'>EXCLUIR</span> | 91.5% | 2 | 0.2% | 0% | 99.8% | `object` | MUITOS NULOS (91.5%) | STRINGS VAZIAS (99.8%) |
| `ConsumoCor5` | <span class='excluir'>EXCLUIR</span> | 100.0% | 2 | 100.0% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) |
| `ViscosidadeCor5` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Cor6` | <span class='excluir'>EXCLUIR</span> | 91.8% | 1 | 0.1% | 0% | 100.0% | `object` | MUITOS NULOS (91.8%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| `ConsumoCor6` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ViscosidadeCor6` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `NrCores` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 57.6% | 0% | `int64` | OK |
| `ImpComRegistro` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 82.6% | 0% | `int64` | MUITOS ZEROS (82.6%) |
| `DetalheCV` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 85.0% | 0% | `int64` | MUITOS ZEROS (85.0%) |
| `TolMais` | <span class='manter'>MANTER</span> | 0.0% | 9 | 0.1% | 1.2% | 0% | `int64` | OK |
| `TolMenos` | <span class='manter'>MANTER</span> | 0.0% | 8 | 0.1% | 0.7% | 0% | `int64` | OK |
| `TipoObs1` | <span class='manter'>MANTER</span> | 32.3% | 12 | 0.2% | 0% | 2.4% | `object` | OK |
| `Obs1` | <span class='manter'>MANTER</span> | 0.1% | 1669 | 15.6% | 0% | 33.9% | `object` | OK |
| `TipoObs2` | <span class='manter'>MANTER</span> | 60.7% | 13 | 0.3% | 0% | 4.9% | `object` | OK |
| `Obs2` | <span class='manter'>MANTER</span> | 3.1% | 1228 | 11.8% | 0% | 61.4% | `object` | OK |
| `TipoObs3` | <span class='manter'>MANTER</span> | 75.1% | 12 | 0.5% | 0% | 7.2% | `object` | OK |
| `Obs3` | <span class='manter'>MANTER</span> | 15.7% | 832 | 9.2% | 0% | 72.5% | `object` | OK |
| `TipoObs4` | <span class='manter'>MANTER</span> | 83.8% | 11 | 0.6% | 0% | 7.0% | `object` | OK |
| `Obs4` | <span class='manter'>MANTER</span> | 24.8% | 624 | 7.8% | 0% | 79.9% | `object` | OK |
| `TipoObs5` | <span class='manter'>MANTER</span> | 88.9% | 10 | 0.8% | 0% | 9.1% | `object` | OK |
| `Obs5` | <span class='excluir'>EXCLUIR</span> | 33.2% | 428 | 6.0% | 0% | 84.8% | `object` | STRINGS VAZIAS (84.8%) |
| `TipoObs6` | <span class='excluir'>EXCLUIR</span> | 93.0% | 10 | 1.3% | 0% | 9.5% | `object` | MUITOS NULOS (93.0%) |
| `Obs6` | <span class='excluir'>EXCLUIR</span> | 38.8% | 312 | 4.8% | 0% | 89.6% | `object` | STRINGS VAZIAS (89.6%) |
| `TipoObs7` | <span class='excluir'>EXCLUIR</span> | 94.6% | 10 | 1.7% | 0% | 11.5% | `object` | MUITOS NULOS (94.6%) |
| `Obs7` | <span class='excluir'>EXCLUIR</span> | 42.8% | 236 | 3.9% | 0% | 91.6% | `object` | STRINGS VAZIAS (91.6%) |
| `TipoObs8` | <span class='excluir'>EXCLUIR</span> | 94.5% | 12 | 2.0% | 0% | 7.7% | `object` | MUITOS NULOS (94.5%) |
| `Obs8` | <span class='excluir'>EXCLUIR</span> | 43.7% | 243 | 4.0% | 0% | 90.9% | `object` | STRINGS VAZIAS (90.9%) |
| `LarguraInterna` | <span class='manter'>MANTER</span> | 0.0% | 502 | 4.7% | 0.1% | 0% | `int64` | OK |
| `ComprimentoInterno` | <span class='manter'>MANTER</span> | 0.0% | 641 | 6.0% | 0.0% | 0% | `int64` | OK |
| `AlturaInterna` | <span class='manter'>MANTER</span> | 1.0% | 486 | 4.6% | 3.9% | 0% | `float64` | OK |
| `LargPeca` | <span class='manter'>MANTER</span> | 0.2% | 1109 | 10.4% | 0.0% | 0% | `float64` | OK |
| `CompPeca` | <span class='manter'>MANTER</span> | 0.2% | 1703 | 15.9% | 0.0% | 0% | `float64` | OK |
| `DimAdic1` | <span class='manter'>MANTER</span> | 86.1% | 115 | 7.7% | 14.9% | 0% | `float64` | OK |
| `DimAdic2` | <span class='manter'>MANTER</span> | 89.0% | 77 | 6.5% | 14.3% | 0% | `float64` | OK |
| `DimAdic3` | <span class='excluir'>EXCLUIR</span> | 97.6% | 84 | 32.6% | 17.4% | 0% | `float64` | MUITOS NULOS (97.6%) |
| `DimAdic4` | <span class='excluir'>EXCLUIR</span> | 98.3% | 12 | 6.7% | 19.4% | 0% | `float64` | MUITOS NULOS (98.3%) |
| `DimAdic5` | <span class='excluir'>EXCLUIR</span> | 98.2% | 48 | 24.7% | 21.1% | 0% | `float64` | MUITOS NULOS (98.2%) |
| `DimAdic6` | <span class='excluir'>EXCLUIR</span> | 98.2% | 54 | 27.8% | 21.1% | 0% | `float64` | MUITOS NULOS (98.2%) |
| `ContraOnda` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| `ImprimeLogotipo` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 9.4% | 0% | `int64` | OK |
| `ComissaoDeVendas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `UsuarioCriacao` | <span class='manter'>MANTER</span> | 0.0% | 8 | 0.1% | 0.0% | 0% | `float64` | OK |
| `Usuario` | <span class='manter'>MANTER</span> | 0.1% | 20 | 0.2% | 0.8% | 0% | `float64` | OK |
| `PesoAdic` | <span class='excluir'>EXCLUIR</span> | 93.9% | 7 | 1.1% | 96.6% | 0% | `float64` | MUITOS NULOS (93.9%) | MUITOS ZEROS (96.6%) |
| `CustoUnitAdic` | <span class='excluir'>EXCLUIR</span> | 99.9% | 1 | 7.7% | 0.0% | 0% | `float64` | MUITOS NULOS (99.9%) | VALOR ÚNICO (35.0) |
| `DataModif` | <span class='manter'>MANTER</span> | 0.0% | 3178 | 29.7% | 0% | 0% | `datetime64[ns]` | OK |
| `DataCriacao` | <span class='manter'>MANTER</span> | 0.0% | 9828 | 91.9% | 0% | 0% | `datetime64[ns]` | OK |
| `CompPacote` | <span class='manter'>MANTER</span> | 4.2% | 1084 | 10.6% | 0.1% | 0% | `float64` | OK |
| `LargPacote` | <span class='manter'>MANTER</span> | 4.2% | 1003 | 9.8% | 0.1% | 0% | `float64` | OK |
| `AlturaPacote` | <span class='manter'>MANTER</span> | 1.9% | 105 | 1.0% | 0.0% | 0% | `float64` | OK |
| `CompPaleteFechado` | <span class='manter'>MANTER</span> | 13.5% | 548 | 5.9% | 0.1% | 0% | `float64` | OK |
| `LargPaleteFechado` | <span class='manter'>MANTER</span> | 13.5% | 515 | 5.6% | 0.1% | 0% | `float64` | OK |
| `AlturaPaleteFechado` | <span class='manter'>MANTER</span> | 2.4% | 134 | 1.3% | 0.0% | 0% | `float64` | OK |
| `PorosidadeMinimo` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PesoCaixa` | <span class='manter'>MANTER</span> | 21.4% | 957 | 11.4% | 0.0% | 0% | `float64` | OK |
| `Projeto` | <span class='manter'>MANTER</span> | 0.7% | 9921 | 93.3% | 0% | 4.8% | `object` | OK |
| `RefiloOnduladeira` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `TipoCustoExtra` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `TravaComposicao` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 86.1% | 0% | `int64` | MUITOS ZEROS (86.1%) |
| `DescrTravaComposicao` | <span class='manter'>MANTER</span> | 62.1% | 185 | 4.6% | 0% | 64.1% | `object` | OK |
| `PrecoNegociado` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `RefiloOndOrcam` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `RefiloCompOrcam` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `GrupoPaletizacao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PathFiguraDoLastro` | <span class='manter'>MANTER</span> | 0.0% | 117 | 1.1% | 0% | 11.6% | `object` | OK |
| `PathFiguraDaFT` | <span class='excluir'>EXCLUIR</span> | 0.1% | 61 | 0.6% | 0% | 95.0% | `object` | STRINGS VAZIAS (95.0%) |
| `PressaoDeArqueamento` | <span class='excluir'>EXCLUIR</span> | 99.3% | 2 | 2.6% | 96.1% | 0% | `float64` | MUITOS NULOS (99.3%) | MUITOS ZEROS (96.1%) |
| `EmpilhamentoMaximo` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 0.0% | 0% | `int64` | OK |
| `IDPalete` | <span class='manter'>MANTER</span> | 1.5% | 67 | 0.6% | 0.0% | 0% | `float64` | OK |
| `ReferenciaGrupoPaletizacao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `CodigoERP` | <span class='excluir'>EXCLUIR</span> | 100.0% | 2 | 50.0% | 0% | 75.0% | `object` | MUITOS NULOS (100.0%) |
| `IDUnicoRegistro` | <span class='manter'>MANTER</span> | 0.0% | 7591 | 71.0% | 0% | 0.0% | `object` | OK |
| `FlagEstoqueOuTerceiros` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `DescFlagEstoqueOuTerceiros` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 0% | 0.0% | `object` | VALOR ÚNICO (0-normal) |
| `NrPedsLotePiloto` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 38.7% | 0% | `int64` | OK |
| `AreaUtilCedidaFaca` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `AreaBrutaPecaComRefilos` | <span class='manter'>MANTER</span> | 0.0% | 7548 | 70.5% | 0.0% | 0% | `float64` | OK |
| `AreaBrutaPeca` | <span class='manter'>MANTER</span> | 0.0% | 7383 | 69.0% | 0.0% | 0% | `float64` | OK |
| `AreaLiquidaPeca` | <span class='manter'>MANTER</span> | 0.0% | 7898 | 73.8% | 0.0% | 0% | `float64` | OK |
| `AreaBrutaChapa` | <span class='manter'>MANTER</span> | 0.0% | 7554 | 70.6% | 0.0% | 0% | `float64` | OK |
| `AreaLiquidaChapa` | <span class='manter'>MANTER</span> | 0.0% | 7447 | 69.6% | 0.0% | 0% | `float64` | OK |
| `VolumePaleteFechadoM3` | <span class='manter'>MANTER</span> | 13.6% | 3543 | 38.3% | 0.2% | 0% | `float64` | OK |
| `VolumePacoteFechadoM3` | <span class='manter'>MANTER</span> | 4.3% | 7059 | 68.9% | 0.3% | 0% | `float64` | OK |
| `idUsuarioAnalise` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PrecoFerramentas` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `QuantPrevista` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (1) |
| `ResumoChapa` | <span class='manter'>MANTER</span> | 0.0% | 10320 | 96.5% | 0.0% | 0% | `int64` | OK |
| `ComplementoChapa` | <span class='manter'>MANTER</span> | 0.0% | 809 | 7.6% | 0.0% | 0% | `int64` | OK |

---

## Critérios de Exclusão Utilizados

- Muitos Nulos: > 90% de valores nulos
- Valor Único: coluna possui apenas 1 valor único
- Muitos Zeros: > 80% de valores zero (para colunas numéricas)
- Strings Vazias: > 80% de strings vazias (para colunas de texto)

Colunas que não atendem a esses critérios são mantidas.
