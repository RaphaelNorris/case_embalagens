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
- **Tabela:** `dbo.Pedidos`
- **Data/Hora:** 2025-09-24 13:35:28
- **Total de Registros:** 384577
- **Total de Colunas:** 274
- **Autor:** Raphael Norris

---

## Filtros Aplicados
- **DataCriacao** >= `2022-01-01`

---

## Query Executada
```sql
SELECT * FROM dbo.Pedidos WHERE DataCriacao >= `2022-01-01`
```


---

## Resumo da Análise

| Métrica | Valor |
|---------|-------|
| Total de Colunas | 274 |
| Colunas para Manter | 143 |
| Colunas para Excluir | 131 |
| Percentual de Exclusão | 47.8% |

---

## Colunas Sugeridas para Exclusão

| # | Coluna | Motivos |
|---|--------|---------|
| 1 | `IDPedVenda` | MUITOS NULOS (100.0%) |
| 2 | `IDItemPedVenda` | MUITOS NULOS (100.0%) |
| 3 | `Suspenso` | MUITOS ZEROS (99.9%) |
| 4 | `IDLoja` | VALOR ÚNICO (1) |
| 5 | `IDLocalEntrega` | MUITOS ZEROS (97.7%) |
| 6 | `IDLocalCobranca` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 7 | `CodigoEAN` | MUITOS NULOS (99.9%) |
| 8 | `idTipoFT` | MUITOS NULOS (94.7%) | VALOR ÚNICO (1.0) |
| 9 | `idTipoFT2` | MUITOS NULOS (99.9%) | VALOR ÚNICO (2.0) |
| 10 | `idTipoFT3` | MUITOS NULOS (100.0%) | VALOR ÚNICO (4.0) |
| 11 | `idTipoFT4` | MUITOS NULOS (100.0%) |
| 12 | `idTipoFT5` | MUITOS NULOS (100.0%) |
| 13 | `CobbInt30Maximo` | MUITOS NULOS (100.0%) |
| 14 | `CobbExt30Maximo` | MUITOS NULOS (100.0%) | VALOR ÚNICO (45.0) |
| 15 | `TesteFisicoAdicional1` | MUITOS NULOS (100.0%) | VALOR ÚNICO (8.5) |
| 16 | `PAT_Interno` | MUITOS NULOS (100.0%) |
| 17 | `PAT_Externo` | MUITOS NULOS (100.0%) |
| 18 | `Umidade` | MUITOS NULOS (100.0%) |
| 19 | `Compressao` | MUITOS NULOS (90.2%) |
| 20 | `ProfundidadeVinco` | MUITOS NULOS (100.0%) |
| 21 | `ForcaDeVinco1` | MUITOS NULOS (100.0%) |
| 22 | `ForcaDeVinco2` | MUITOS NULOS (100.0%) |
| 23 | `ForcaDeVinco3` | MUITOS NULOS (100.0%) |
| 24 | `FormatoSimplex` | MUITOS NULOS (99.7%) | MUITOS ZEROS (97.9%) |
| 25 | `VincosLargNoRiscador` | MUITOS ZEROS (98.9%) |
| 26 | `VincoLarg4` | MUITOS ZEROS (97.5%) |
| 27 | `VincoLarg5` | MUITOS ZEROS (98.0%) |
| 28 | `VincoLarg6` | MUITOS ZEROS (100.0%) |
| 29 | `VincoLarg7` | MUITOS ZEROS (100.0%) |
| 30 | `VincoLarg8` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 31 | `VincoLarg9` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 32 | `VincoLarg10` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 33 | `VincosCompNoRiscador` | MUITOS ZEROS (98.8%) |
| 34 | `VincoComp6` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 35 | `VincoComp7` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 36 | `VincoComp8` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 37 | `VincoComp9` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 38 | `VincoComp10` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 39 | `TearTape1` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 40 | `TearTape2` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 41 | `TearTape3` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 42 | `TearTape4` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 43 | `ProlongLap` | MUITOS ZEROS (92.7%) |
| 44 | `Rejeito` | MUITOS ZEROS (98.7%) |
| 45 | `RejeitoPecas` | MUITOS ZEROS (100.0%) |
| 46 | `ResinaExterna` | MUITOS ZEROS (100.0%) |
| 47 | `ResinaExternaSN` | MUITOS ZEROS (100.0%) |
| 48 | `EndurecedorMiolo` | MUITOS NULOS (99.5%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| 49 | `EndurecedorMioloSN` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 50 | `Grampos` | MUITOS ZEROS (99.0%) |
| 51 | `FitilhosCompPacote` | MUITOS ZEROS (97.6%) |
| 52 | `FacesOpostas` | MUITOS ZEROS (99.6%) |
| 53 | `Cantoneiras` | MUITOS ZEROS (96.1%) |
| 54 | `OrelhasInvertidas` | MUITOS ZEROS (97.6%) |
| 55 | `ViscosidadeCor1` | MUITOS NULOS (100.0%) |
| 56 | `ViscosidadeCor2` | MUITOS NULOS (100.0%) |
| 57 | `Cor3` | STRINGS VAZIAS (82.3%) |
| 58 | `ViscosidadeCor3` | MUITOS NULOS (100.0%) |
| 59 | `Cor4` | STRINGS VAZIAS (83.6%) |
| 60 | `ConsumoCor4` | MUITOS NULOS (90.2%) |
| 61 | `ViscosidadeCor4` | MUITOS NULOS (100.0%) |
| 62 | `Cor5` | MUITOS NULOS (96.7%) | STRINGS VAZIAS (99.7%) |
| 63 | `ConsumoCor5` | MUITOS NULOS (100.0%) |
| 64 | `ViscosidadeCor5` | MUITOS NULOS (100.0%) |
| 65 | `Cor6` | MUITOS NULOS (95.9%) |
| 66 | `ConsumoCor6` | MUITOS NULOS (100.0%) |
| 67 | `ViscosidadeCor6` | MUITOS NULOS (100.0%) |
| 68 | `ImpComRegistro` | MUITOS ZEROS (85.7%) |
| 69 | `DetalheCV` | MUITOS ZEROS (93.7%) |
| 70 | `ContraOnda` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| 71 | `TipoObs7` | MUITOS NULOS (91.9%) |
| 72 | `Obs7` | STRINGS VAZIAS (83.3%) |
| 73 | `TipoObs8` | MUITOS NULOS (92.0%) |
| 74 | `Obs8` | STRINGS VAZIAS (82.5%) |
| 75 | `DimAdic1` | MUITOS NULOS (91.9%) |
| 76 | `DimAdic2` | MUITOS NULOS (92.8%) |
| 77 | `DimAdic3` | MUITOS NULOS (99.0%) |
| 78 | `DimAdic4` | MUITOS NULOS (99.2%) |
| 79 | `DimAdic5` | MUITOS NULOS (99.0%) |
| 80 | `DimAdic6` | MUITOS NULOS (99.0%) |
| 81 | `PrecoUnitVenda` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 82 | `CustoUnitTransp` | MUITOS NULOS (100.0%) |
| 83 | `CustoUnitVar` | MUITOS NULOS (100.0%) |
| 84 | `CustoUnitFixo` | MUITOS NULOS (100.0%) |
| 85 | `ResultOperacional` | MUITOS NULOS (100.0%) |
| 86 | `MargemContrHora` | MUITOS NULOS (100.0%) |
| 87 | `ReceitaLiquida` | MUITOS NULOS (100.0%) |
| 88 | `VendaLiquida` | MUITOS NULOS (100.0%) |
| 89 | `MargemContr` | MUITOS NULOS (100.0%) |
| 90 | `PesoAdic` | MUITOS NULOS (92.4%) | MUITOS ZEROS (99.8%) |
| 91 | `CustoUnitAdic` | MUITOS NULOS (100.0%) |
| 92 | `RegiaoOrigem` | MUITOS NULOS (100.0%) |
| 93 | `FreteIncluso` | MUITOS NULOS (99.9%) | VALOR ÚNICO (1.0) |
| 94 | `NrDeCarros` | MUITOS NULOS (100.0%) |
| 95 | `CustoExtraFrete` | MUITOS NULOS (100.0%) |
| 96 | `PrecoFrete` | MUITOS NULOS (99.9%) | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 97 | `PrecoFerramentas` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 98 | `QuantPrevista` | VALOR ÚNICO (1) |
| 99 | `NivelUrgencia` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 100 | `FlagEstoqueOuTerceiros` | MUITOS ZEROS (99.2%) |
| 101 | `Adicional1` | VALOR ÚNICO (0) |
| 102 | `PossivelDataEntrega` | MUITOS NULOS (100.0%) |
| 103 | `TipoDoPedido` | MUITOS ZEROS (86.9%) |
| 104 | `TempoExpedViagem` | MUITOS NULOS (100.0%) |
| 105 | `ComissaoDeVendas` | MUITOS NULOS (99.9%) | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 106 | `VersaoDeCusto` | MUITOS NULOS (99.9%) | VALOR ÚNICO (7.0) |
| 107 | `PorosidadeMinimo` | MUITOS NULOS (100.0%) |
| 108 | `RefiloOnduladeira` | MUITOS NULOS (100.0%) |
| 109 | `TipoCustoExtra` | MUITOS NULOS (100.0%) |
| 110 | `ItemPedCliente` | MUITOS NULOS (100.0%) |
| 111 | `TipoCaminhao` | MUITOS NULOS (99.9%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| 112 | `Conjunto` | MUITOS NULOS (99.2%) |
| 113 | `TravaComposicao` | MUITOS ZEROS (80.4%) |
| 114 | `DataPromessa` | MUITOS NULOS (100.0%) |
| 115 | `PrecoReferencia` | MUITOS NULOS (100.0%) |
| 116 | `PathFiguraDaFT` | STRINGS VAZIAS (92.4%) |
| 117 | `PressaoDeArqueamento` | MUITOS NULOS (99.9%) | MUITOS ZEROS (82.4%) |
| 118 | `GrupoPaletizacao` | MUITOS NULOS (100.0%) |
| 119 | `LiberadoProgExped` | VALOR ÚNICO (1) |
| 120 | `ReferenciaGrupoPaletizacao` | MUITOS NULOS (100.0%) |
| 121 | `LotePiloto` | MUITOS ZEROS (98.9%) |
| 122 | `ObsAlteracoes` | MUITOS NULOS (98.4%) |
| 123 | `Orcamento` | MUITOS NULOS (100.0%) |
| 124 | `ItemOrcamento` | MUITOS NULOS (100.0%) |
| 125 | `AreaUtilCedidaFaca` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 126 | `idFilialExpedicao` | VALOR ÚNICO (1.0) |
| 127 | `QtdImpressoes` | MUITOS ZEROS (100.0%) |
| 128 | `DataHoraPrimeiraImpressao` | MUITOS NULOS (100.0%) |
| 129 | `IDUsuarioPrimeiraImpressao` | MUITOS NULOS (100.0%) |
| 130 | `DataHoraUltimaImpressao` | MUITOS NULOS (100.0%) |
| 131 | `IDUsuarioUltimaImpressao` | MUITOS NULOS (100.0%) |

---

## Análise Detalhada de Todas as Colunas

| Coluna | Ação | Nulos (%) | Valores Únicos | Variância (%) | Zeros (%) | Vazias (%) | Tipo | Motivos |
|--------|------|-----------|----------------|---------------|-----------|------------|------|---------|
| `IDPedidos` | <span class='manter'>MANTER</span> | 0.0% | 384577 | 100.0% | 0.0% | 0% | `int64` | OK |
| `Pedido` | <span class='manter'>MANTER</span> | 0.0% | 383196 | 99.6% | 0% | 0.0% | `object` | OK |
| `Item` | <span class='manter'>MANTER</span> | 0.0% | 29748 | 7.7% | 0% | 0.0% | `object` | OK |
| `ItemPedido` | <span class='manter'>MANTER</span> | 0.0% | 238 | 0.1% | 0% | 0.0% | `object` | OK |
| `IDPedVenda` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `IDItemPedVenda` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `StatusPedido` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 0.0% | 0% | `int64` | OK |
| `DescrStatusPedido` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 0% | 0.0% | `object` | OK |
| `Suspenso` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 99.9% | 0% | `int64` | MUITOS ZEROS (99.9%) |
| `SuspOuCancel` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 0% | 0.0% | `object` | OK |
| `Versao` | <span class='manter'>MANTER</span> | 0.0% | 170 | 0.0% | 21.3% | 0% | `int64` | OK |
| `IDCliente` | <span class='manter'>MANTER</span> | 0.0% | 1127 | 0.3% | 0.0% | 0% | `int64` | OK |
| `IDLoja` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (1) |
| `IDLocalEntrega` | <span class='excluir'>EXCLUIR</span> | 0.0% | 16 | 0.0% | 97.7% | 0% | `int64` | MUITOS ZEROS (97.7%) |
| `IDLocalCobranca` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `Referencia` | <span class='manter'>MANTER</span> | 0.0% | 31087 | 8.1% | 0% | 0.0% | `object` | OK |
| `CodigoReferencia` | <span class='manter'>MANTER</span> | 31.8% | 3407 | 1.3% | 0% | 5.7% | `object` | OK |
| `CodigoEAN` | <span class='excluir'>EXCLUIR</span> | 99.9% | 2 | 0.8% | 0% | 2.4% | `object` | MUITOS NULOS (99.9%) |
| `TipoABNT` | <span class='manter'>MANTER</span> | 0.0% | 103 | 0.0% | 0% | 0.0% | `object` | OK |
| `idTipoFT` | <span class='excluir'>EXCLUIR</span> | 94.7% | 1 | 0.0% | 0.0% | 0% | `float64` | MUITOS NULOS (94.7%) | VALOR ÚNICO (1.0) |
| `idTipoFT2` | <span class='excluir'>EXCLUIR</span> | 99.9% | 1 | 0.4% | 0.0% | 0% | `float64` | MUITOS NULOS (99.9%) | VALOR ÚNICO (2.0) |
| `idTipoFT3` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 0.5% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) | VALOR ÚNICO (4.0) |
| `idTipoFT4` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `idTipoFT5` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PecasPorUnidade` | <span class='manter'>MANTER</span> | 0.0% | 3 | 0.0% | 0.0% | 0% | `float64` | OK |
| `UnidadesPorConjunto` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 0.0% | 0% | `float64` | OK |
| `PecasPorConjunto` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 0.0% | 0% | `float64` | OK |
| `ExigeLaudo` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 12.2% | 0% | `int64` | OK |
| `Gramatura` | <span class='manter'>MANTER</span> | 3.6% | 209 | 0.1% | 0.0% | 0% | `float64` | OK |
| `MullenMinimo` | <span class='manter'>MANTER</span> | 28.5% | 42 | 0.0% | 0.0% | 0% | `float64` | OK |
| `CrushMinimo` | <span class='manter'>MANTER</span> | 76.5% | 19 | 0.0% | 0.0% | 0% | `float64` | OK |
| `ColunaMinimo` | <span class='manter'>MANTER</span> | 2.6% | 60 | 0.0% | 0.0% | 0% | `float64` | OK |
| `CobbIntMaximo` | <span class='manter'>MANTER</span> | 26.5% | 18 | 0.0% | 0.0% | 0% | `float64` | OK |
| `CobbExtMaximo` | <span class='manter'>MANTER</span> | 26.8% | 15 | 0.0% | 0.0% | 0% | `float64` | OK |
| `CobbInt30Maximo` | <span class='excluir'>EXCLUIR</span> | 100.0% | 2 | 33.3% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) |
| `CobbExt30Maximo` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 100.0% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) | VALOR ÚNICO (45.0) |
| `TesteFisicoAdicional1` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 9.1% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) | VALOR ÚNICO (8.5) |
| `PAT_Interno` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PAT_Externo` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Espessura` | <span class='manter'>MANTER</span> | 3.3% | 65 | 0.0% | 0.0% | 0% | `float64` | OK |
| `Umidade` | <span class='excluir'>EXCLUIR</span> | 100.0% | 3 | 20.0% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) |
| `Compressao` | <span class='excluir'>EXCLUIR</span> | 90.2% | 134 | 0.4% | 0.0% | 0% | `float64` | MUITOS NULOS (90.2%) |
| `ProfundidadeVinco` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ForcaDeVinco1` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ForcaDeVinco2` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ForcaDeVinco3` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Chapa` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 78.4% | 0% | `int64` | OK |
| `Composicao` | <span class='manter'>MANTER</span> | 0.0% | 70 | 0.0% | 0% | 0.0% | `object` | OK |
| `FormatoSimplex` | <span class='excluir'>EXCLUIR</span> | 99.7% | 3 | 0.3% | 97.9% | 0% | `float64` | MUITOS NULOS (99.7%) | MUITOS ZEROS (97.9%) |
| `Largura` | <span class='manter'>MANTER</span> | 0.0% | 1741 | 0.5% | 0.0% | 0% | `int64` | OK |
| `RefiloLargura` | <span class='manter'>MANTER</span> | 0.0% | 35 | 0.0% | 44.3% | 0% | `int64` | OK |
| `Comprimento` | <span class='manter'>MANTER</span> | 0.0% | 2064 | 0.5% | 0.0% | 0% | `int64` | OK |
| `RefiloComprimento` | <span class='manter'>MANTER</span> | 0.0% | 18 | 0.0% | 43.2% | 0% | `int64` | OK |
| `MultLarg` | <span class='manter'>MANTER</span> | 0.0% | 9 | 0.0% | 0.0% | 0% | `int64` | OK |
| `MultComp` | <span class='manter'>MANTER</span> | 0.0% | 7 | 0.0% | 0.0% | 0% | `int64` | OK |
| `Arranjo` | <span class='manter'>MANTER</span> | 0.0% | 17 | 0.0% | 0.0% | 0% | `int64` | OK |
| `RefugoCliente` | <span class='manter'>MANTER</span> | 0.0% | 4448 | 1.2% | 23.4% | 0% | `float64` | OK |
| `PesoPeca` | <span class='manter'>MANTER</span> | 67.9% | 3898 | 3.2% | 0.0% | 0% | `float64` | OK |
| `VincosLargNoRiscador` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 98.9% | 0% | `bool` | MUITOS ZEROS (98.9%) |
| `VincoLarg1` | <span class='manter'>MANTER</span> | 39.3% | 479 | 0.2% | 49.5% | 0% | `float64` | OK |
| `VincoLarg2` | <span class='manter'>MANTER</span> | 39.3% | 1009 | 0.4% | 49.5% | 0% | `float64` | OK |
| `VincoLarg3` | <span class='manter'>MANTER</span> | 40.4% | 658 | 0.3% | 50.7% | 0% | `float64` | OK |
| `VincoLarg4` | <span class='excluir'>EXCLUIR</span> | 60.4% | 374 | 0.2% | 97.5% | 0% | `float64` | MUITOS ZEROS (97.5%) |
| `VincoLarg5` | <span class='excluir'>EXCLUIR</span> | 60.5% | 381 | 0.3% | 98.0% | 0% | `float64` | MUITOS ZEROS (98.0%) |
| `VincoLarg6` | <span class='excluir'>EXCLUIR</span> | 60.5% | 25 | 0.0% | 100.0% | 0% | `float64` | MUITOS ZEROS (100.0%) |
| `VincoLarg7` | <span class='excluir'>EXCLUIR</span> | 60.5% | 2 | 0.0% | 100.0% | 0% | `float64` | MUITOS ZEROS (100.0%) |
| `VincoLarg8` | <span class='excluir'>EXCLUIR</span> | 60.5% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `VincoLarg9` | <span class='excluir'>EXCLUIR</span> | 60.5% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `VincoLarg10` | <span class='excluir'>EXCLUIR</span> | 81.8% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `VincosCompNoRiscador` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 98.8% | 0% | `bool` | MUITOS ZEROS (98.8%) |
| `VincoComp1` | <span class='manter'>MANTER</span> | 60.4% | 43 | 0.0% | 45.7% | 0% | `float64` | OK |
| `VincoComp2` | <span class='manter'>MANTER</span> | 60.4% | 367 | 0.2% | 45.7% | 0% | `float64` | OK |
| `VincoComp3` | <span class='manter'>MANTER</span> | 60.5% | 475 | 0.3% | 45.8% | 0% | `float64` | OK |
| `VincoComp4` | <span class='manter'>MANTER</span> | 60.8% | 350 | 0.2% | 46.2% | 0% | `float64` | OK |
| `VincoComp5` | <span class='manter'>MANTER</span> | 60.8% | 442 | 0.3% | 46.2% | 0% | `float64` | OK |
| `VincoComp6` | <span class='excluir'>EXCLUIR</span> | 81.8% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `VincoComp7` | <span class='excluir'>EXCLUIR</span> | 81.8% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `VincoComp8` | <span class='excluir'>EXCLUIR</span> | 81.8% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `VincoComp9` | <span class='excluir'>EXCLUIR</span> | 81.8% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `VincoComp10` | <span class='excluir'>EXCLUIR</span> | 81.8% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `TearTape1` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `TearTape2` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `TearTape3` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `TearTape4` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `Lap` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 78.3% | 0% | `int64` | OK |
| `ProlongLap` | <span class='excluir'>EXCLUIR</span> | 0.0% | 3 | 0.0% | 92.7% | 0% | `int64` | MUITOS ZEROS (92.7%) |
| `LapNoComp` | <span class='manter'>MANTER</span> | 0.0% | 3 | 0.0% | 19.5% | 0% | `int64` | OK |
| `LapInterno` | <span class='manter'>MANTER</span> | 0.0% | 3 | 0.0% | 0.6% | 0% | `int64` | OK |
| `LapPrimVinco` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 57.5% | 0% | `int64` | OK |
| `Refilado` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 0.2% | 0% | `int64` | OK |
| `Rejeito` | <span class='excluir'>EXCLUIR</span> | 0.0% | 3 | 0.0% | 98.7% | 0% | `int64` | MUITOS ZEROS (98.7%) |
| `RejeitoPecas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 100.0% | 0% | `int64` | MUITOS ZEROS (100.0%) |
| `ResinaInterna` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 77.8% | 0% | `int64` | OK |
| `ResinaInternaSN` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 77.8% | 0% | `int64` | OK |
| `ResinaExterna` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 100.0% | 0% | `int64` | MUITOS ZEROS (100.0%) |
| `ResinaExternaSN` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 100.0% | 0% | `int64` | MUITOS ZEROS (100.0%) |
| `EndurecedorMiolo` | <span class='excluir'>EXCLUIR</span> | 99.5% | 1 | 0.1% | 0% | 100.0% | `object` | MUITOS NULOS (99.5%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| `EndurecedorMioloSN` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `Fechamento` | <span class='manter'>MANTER</span> | 24.2% | 16 | 0.0% | 0% | 0.2% | `object` | OK |
| `Grampos` | <span class='excluir'>EXCLUIR</span> | 84.4% | 18 | 0.0% | 99.0% | 0% | `float64` | MUITOS ZEROS (99.0%) |
| `Amarrado` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 28.1% | 0% | `int64` | OK |
| `FitilhosLargPacote` | <span class='manter'>MANTER</span> | 21.8% | 3 | 0.0% | 10.4% | 0% | `float64` | OK |
| `FitilhosCompPacote` | <span class='excluir'>EXCLUIR</span> | 24.6% | 3 | 0.0% | 97.6% | 0% | `float64` | MUITOS ZEROS (97.6%) |
| `Paletizado` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 21.9% | 0% | `int64` | OK |
| `DescrPaletizado` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 0% | 0.0% | `object` | OK |
| `PacotesLargura` | <span class='manter'>MANTER</span> | 21.5% | 12 | 0.0% | 0.0% | 0% | `float64` | OK |
| `PacotesComprimento` | <span class='manter'>MANTER</span> | 21.5% | 15 | 0.0% | 0.0% | 0% | `float64` | OK |
| `PacotesAltura` | <span class='manter'>MANTER</span> | 21.3% | 36 | 0.0% | 0.0% | 0% | `float64` | OK |
| `PecasPorPacote` | <span class='manter'>MANTER</span> | 21.3% | 32 | 0.0% | 0.1% | 0% | `float64` | OK |
| `PecasPorPalete` | <span class='manter'>MANTER</span> | 21.5% | 168 | 0.1% | 0.1% | 0% | `float64` | OK |
| `UnidadesPorPalete` | <span class='manter'>MANTER</span> | 21.5% | 168 | 0.1% | 0.1% | 0% | `float64` | OK |
| `PacotesPorPalete` | <span class='manter'>MANTER</span> | 21.5% | 109 | 0.0% | 0.0% | 0% | `float64` | OK |
| `FitasLargPalete` | <span class='manter'>MANTER</span> | 21.7% | 4 | 0.0% | 0.9% | 0% | `float64` | OK |
| `FitasCompPalete` | <span class='manter'>MANTER</span> | 21.7% | 4 | 0.0% | 0.2% | 0% | `float64` | OK |
| `FacesOpostas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 99.6% | 0% | `int64` | MUITOS ZEROS (99.6%) |
| `Espelho` | <span class='manter'>MANTER</span> | 0.0% | 7 | 0.0% | 22.9% | 0% | `int64` | OK |
| `Cantoneiras` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 96.1% | 0% | `int64` | MUITOS ZEROS (96.1%) |
| `Filme` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 22.6% | 0% | `int64` | OK |
| `OrelhasInvertidas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 97.6% | 0% | `int64` | MUITOS ZEROS (97.6%) |
| `Faca` | <span class='manter'>MANTER</span> | 37.4% | 2476 | 1.0% | 0% | 0.2% | `object` | OK |
| `CodFI` | <span class='manter'>MANTER</span> | 24.0% | 5915 | 2.0% | 0% | 0.0% | `object` | OK |
| `Cor1` | <span class='manter'>MANTER</span> | 26.4% | 123 | 0.0% | 0% | 9.9% | `object` | OK |
| `ConsumoCor1` | <span class='manter'>MANTER</span> | 34.9% | 2300 | 0.9% | 0.2% | 0% | `float64` | OK |
| `ViscosidadeCor1` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Cor2` | <span class='manter'>MANTER</span> | 27.6% | 135 | 0.0% | 0% | 70.3% | `object` | OK |
| `ConsumoCor2` | <span class='manter'>MANTER</span> | 79.1% | 2108 | 2.6% | 0.0% | 0% | `float64` | OK |
| `ViscosidadeCor2` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Cor3` | <span class='excluir'>EXCLUIR</span> | 32.4% | 127 | 0.0% | 0% | 82.3% | `object` | STRINGS VAZIAS (82.3%) |
| `ConsumoCor3` | <span class='manter'>MANTER</span> | 88.3% | 1763 | 3.9% | 0.0% | 0% | `float64` | OK |
| `ViscosidadeCor3` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Cor4` | <span class='excluir'>EXCLUIR</span> | 39.2% | 98 | 0.0% | 0% | 83.6% | `object` | STRINGS VAZIAS (83.6%) |
| `ConsumoCor4` | <span class='excluir'>EXCLUIR</span> | 90.2% | 1256 | 3.3% | 0.3% | 0% | `float64` | MUITOS NULOS (90.2%) |
| `ViscosidadeCor4` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Cor5` | <span class='excluir'>EXCLUIR</span> | 96.7% | 3 | 0.0% | 0% | 99.7% | `object` | MUITOS NULOS (96.7%) | STRINGS VAZIAS (99.7%) |
| `ConsumoCor5` | <span class='excluir'>EXCLUIR</span> | 100.0% | 6 | 17.1% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) |
| `ViscosidadeCor5` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Cor6` | <span class='excluir'>EXCLUIR</span> | 95.9% | 2 | 0.0% | 0% | 74.6% | `object` | MUITOS NULOS (95.9%) |
| `ConsumoCor6` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ViscosidadeCor6` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `NrCores` | <span class='manter'>MANTER</span> | 0.0% | 6 | 0.0% | 25.1% | 0% | `int64` | OK |
| `ImpComRegistro` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 85.7% | 0% | `int64` | MUITOS ZEROS (85.7%) |
| `DetalheCV` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 93.7% | 0% | `int64` | MUITOS ZEROS (93.7%) |
| `TolMais` | <span class='manter'>MANTER</span> | 0.0% | 12 | 0.0% | 0.8% | 0% | `int64` | OK |
| `TolMenos` | <span class='manter'>MANTER</span> | 0.0% | 14 | 0.0% | 0.4% | 0% | `int64` | OK |
| `ContraOnda` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| `TipoObs1` | <span class='manter'>MANTER</span> | 37.9% | 14 | 0.0% | 0% | 6.4% | `object` | OK |
| `Obs1` | <span class='manter'>MANTER</span> | 21.2% | 2516 | 0.8% | 0% | 26.3% | `object` | OK |
| `TipoObs2` | <span class='manter'>MANTER</span> | 52.1% | 16 | 0.0% | 0% | 6.4% | `object` | OK |
| `Obs2` | <span class='manter'>MANTER</span> | 23.0% | 1926 | 0.7% | 0% | 41.7% | `object` | OK |
| `TipoObs3` | <span class='manter'>MANTER</span> | 65.2% | 14 | 0.0% | 0% | 11.5% | `object` | OK |
| `Obs3` | <span class='manter'>MANTER</span> | 28.7% | 1536 | 0.6% | 0% | 56.8% | `object` | OK |
| `TipoObs4` | <span class='manter'>MANTER</span> | 77.2% | 12 | 0.0% | 0% | 6.2% | `object` | OK |
| `Obs4` | <span class='manter'>MANTER</span> | 36.4% | 1113 | 0.5% | 0% | 66.3% | `object` | OK |
| `TipoObs5` | <span class='manter'>MANTER</span> | 84.5% | 12 | 0.0% | 0% | 8.9% | `object` | OK |
| `Obs5` | <span class='manter'>MANTER</span> | 41.1% | 784 | 0.3% | 0% | 76.1% | `object` | OK |
| `TipoObs6` | <span class='manter'>MANTER</span> | 88.9% | 14 | 0.0% | 0% | 5.6% | `object` | OK |
| `Obs6` | <span class='manter'>MANTER</span> | 48.9% | 520 | 0.3% | 0% | 79.5% | `object` | OK |
| `TipoObs7` | <span class='excluir'>EXCLUIR</span> | 91.9% | 11 | 0.0% | 0% | 6.3% | `object` | MUITOS NULOS (91.9%) |
| `Obs7` | <span class='excluir'>EXCLUIR</span> | 53.4% | 389 | 0.2% | 0% | 83.3% | `object` | STRINGS VAZIAS (83.3%) |
| `TipoObs8` | <span class='excluir'>EXCLUIR</span> | 92.0% | 11 | 0.0% | 0% | 3.1% | `object` | MUITOS NULOS (92.0%) |
| `Obs8` | <span class='excluir'>EXCLUIR</span> | 55.6% | 328 | 0.2% | 0% | 82.5% | `object` | STRINGS VAZIAS (82.5%) |
| `TipoObs9` | <span class='manter'>MANTER</span> | 78.5% | 6 | 0.0% | 0% | 0.0% | `object` | OK |
| `Obs9` | <span class='manter'>MANTER</span> | 0.1% | 565 | 0.1% | 0% | 78.4% | `object` | OK |
| `DataEntrega1` | <span class='manter'>MANTER</span> | 0.0% | 1374 | 0.4% | 0% | 0% | `datetime64[ns]` | OK |
| `DataEntrega2` | <span class='manter'>MANTER</span> | 0.0% | 1374 | 0.4% | 0% | 0% | `datetime64[ns]` | OK |
| `QuantidadePedida` | <span class='manter'>MANTER</span> | 0.0% | 14809 | 3.9% | 0.0% | 0% | `int64` | OK |
| `QuantidadePedidaMin` | <span class='manter'>MANTER</span> | 0.0% | 17232 | 4.5% | 0.0% | 0% | `int64` | OK |
| `QuantidadePedidaMax` | <span class='manter'>MANTER</span> | 0.0% | 17772 | 4.6% | 0.0% | 0% | `int64` | OK |
| `TipoEntrega` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 59.2% | 0% | `int64` | OK |
| `DescTipoEntrega` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 0% | 0.0% | `object` | OK |
| `LarguraInterna` | <span class='manter'>MANTER</span> | 21.3% | 441 | 0.1% | 0.1% | 0% | `float64` | OK |
| `ComprimentoInterno` | <span class='manter'>MANTER</span> | 21.3% | 554 | 0.2% | 0.1% | 0% | `float64` | OK |
| `AlturaInterna` | <span class='manter'>MANTER</span> | 21.5% | 455 | 0.2% | 2.1% | 0% | `float64` | OK |
| `LargPeca` | <span class='manter'>MANTER</span> | 21.3% | 1007 | 0.3% | 0.0% | 0% | `float64` | OK |
| `CompPeca` | <span class='manter'>MANTER</span> | 21.3% | 1505 | 0.5% | 0.0% | 0% | `float64` | OK |
| `DimAdic1` | <span class='excluir'>EXCLUIR</span> | 91.9% | 98 | 0.3% | 10.5% | 0% | `float64` | MUITOS NULOS (91.9%) |
| `DimAdic2` | <span class='excluir'>EXCLUIR</span> | 92.8% | 73 | 0.3% | 18.1% | 0% | `float64` | MUITOS NULOS (92.8%) |
| `DimAdic3` | <span class='excluir'>EXCLUIR</span> | 99.0% | 74 | 1.9% | 14.3% | 0% | `float64` | MUITOS NULOS (99.0%) |
| `DimAdic4` | <span class='excluir'>EXCLUIR</span> | 99.2% | 17 | 0.6% | 15.5% | 0% | `float64` | MUITOS NULOS (99.2%) |
| `DimAdic5` | <span class='excluir'>EXCLUIR</span> | 99.0% | 42 | 1.1% | 17.7% | 0% | `float64` | MUITOS NULOS (99.0%) |
| `DimAdic6` | <span class='excluir'>EXCLUIR</span> | 99.0% | 45 | 1.2% | 17.7% | 0% | `float64` | MUITOS NULOS (99.0%) |
| `PrecoUnitVenda` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `CustoUnitTransp` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `CustoUnitVar` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `CustoUnitFixo` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ResultOperacional` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `MargemContrHora` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ReceitaLiquida` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `VendaLiquida` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `MargemContr` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PesoAdic` | <span class='excluir'>EXCLUIR</span> | 92.4% | 6 | 0.0% | 99.8% | 0% | `float64` | MUITOS NULOS (92.4%) | MUITOS ZEROS (99.8%) |
| `CustoUnitAdic` | <span class='excluir'>EXCLUIR</span> | 100.0% | 2 | 2.2% | 67.8% | 0% | `float64` | MUITOS NULOS (100.0%) |
| `RegiaoOrigem` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Distancia` | <span class='manter'>MANTER</span> | 0.3% | 296 | 0.1% | 0.0% | 0% | `float64` | OK |
| `FreteIncluso` | <span class='excluir'>EXCLUIR</span> | 99.9% | 1 | 0.5% | 0.0% | 0% | `float64` | MUITOS NULOS (99.9%) | VALOR ÚNICO (1.0) |
| `CondicaoDePagamento` | <span class='manter'>MANTER</span> | 0.1% | 133 | 0.0% | 0% | 0.0% | `object` | OK |
| `NrDeCarros` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `CustoExtraFrete` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PrecoFrete` | <span class='excluir'>EXCLUIR</span> | 99.9% | 1 | 0.5% | 100.0% | 0% | `float64` | MUITOS NULOS (99.9%) | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `PrecoFerramentas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `QuantPrevista` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (1) |
| `DataCriacao` | <span class='manter'>MANTER</span> | 0.0% | 58800 | 15.3% | 0% | 0% | `datetime64[ns]` | OK |
| `DataEntregaOriginal` | <span class='manter'>MANTER</span> | 0.0% | 1383 | 0.4% | 0% | 0% | `datetime64[ns]` | OK |
| `NivelUrgencia` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `DataUltimaAlteracaoFT` | <span class='manter'>MANTER</span> | 21.3% | 32482 | 10.7% | 0% | 0% | `datetime64[ns]` | OK |
| `FlagEstoqueOuTerceiros` | <span class='excluir'>EXCLUIR</span> | 0.0% | 3 | 0.0% | 99.2% | 0% | `int64` | MUITOS ZEROS (99.2%) |
| `DescFlagEstoqueOuTerceiros` | <span class='manter'>MANTER</span> | 0.0% | 3 | 0.0% | 0% | 0.0% | `object` | OK |
| `Adicional1` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 0% | 0.0% | `object` | VALOR ÚNICO (0) |
| `PossivelDataEntrega` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `TipoDoPedido` | <span class='excluir'>EXCLUIR</span> | 0.0% | 4 | 0.0% | 86.9% | 0% | `int64` | MUITOS ZEROS (86.9%) |
| `DescrTipoDoPedido` | <span class='manter'>MANTER</span> | 0.0% | 4 | 0.0% | 0% | 0.0% | `object` | OK |
| `TempoExpedViagem` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ImprimeLogotipo` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 3.7% | 0% | `int64` | OK |
| `ComissaoDeVendas` | <span class='excluir'>EXCLUIR</span> | 99.9% | 1 | 0.5% | 100.0% | 0% | `float64` | MUITOS NULOS (99.9%) | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `VersaoDeCusto` | <span class='excluir'>EXCLUIR</span> | 99.9% | 1 | 0.5% | 0.0% | 0% | `float64` | MUITOS NULOS (99.9%) | VALOR ÚNICO (7.0) |
| `CompPacote` | <span class='manter'>MANTER</span> | 21.4% | 1029 | 0.3% | 0.0% | 0% | `float64` | OK |
| `LargPacote` | <span class='manter'>MANTER</span> | 21.4% | 939 | 0.3% | 0.0% | 0% | `float64` | OK |
| `AlturaPacote` | <span class='manter'>MANTER</span> | 21.4% | 133 | 0.0% | 0.0% | 0% | `float64` | OK |
| `CompPaleteFechado` | <span class='manter'>MANTER</span> | 21.6% | 581 | 0.2% | 0.0% | 0% | `float64` | OK |
| `LargPaleteFechado` | <span class='manter'>MANTER</span> | 21.6% | 541 | 0.2% | 0.0% | 0% | `float64` | OK |
| `AlturaPaleteFechado` | <span class='manter'>MANTER</span> | 21.5% | 181 | 0.1% | 0.0% | 0% | `float64` | OK |
| `PorosidadeMinimo` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PesoCaixa` | <span class='manter'>MANTER</span> | 25.2% | 858 | 0.3% | 0.0% | 0% | `float64` | OK |
| `RefiloOnduladeira` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `TipoCustoExtra` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PedCliente` | <span class='manter'>MANTER</span> | 0.1% | 294943 | 76.7% | 0% | 0.0% | `object` | OK |
| `ItemPedCliente` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `TipoCaminhao` | <span class='excluir'>EXCLUIR</span> | 99.9% | 1 | 0.5% | 0% | 100.0% | `object` | MUITOS NULOS (99.9%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| `Conjunto` | <span class='excluir'>EXCLUIR</span> | 99.2% | 82 | 2.8% | 0% | 0.0% | `object` | MUITOS NULOS (99.2%) |
| `TravaComposicao` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 80.4% | 0% | `int64` | MUITOS ZEROS (80.4%) |
| `DescrTravaComposicao` | <span class='manter'>MANTER</span> | 65.2% | 406 | 0.3% | 0% | 46.7% | `object` | OK |
| `DataPromessa` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PrecoReferencia` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PathFiguraDoLastro` | <span class='manter'>MANTER</span> | 21.3% | 115 | 0.0% | 0% | 0.4% | `object` | OK |
| `PathFiguraDaFT` | <span class='excluir'>EXCLUIR</span> | 21.4% | 69 | 0.0% | 0% | 92.4% | `object` | STRINGS VAZIAS (92.4%) |
| `PressaoDeArqueamento` | <span class='excluir'>EXCLUIR</span> | 99.9% | 2 | 1.0% | 82.4% | 0% | `float64` | MUITOS NULOS (99.9%) | MUITOS ZEROS (82.4%) |
| `EmpilhamentoMaximo` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 0.0% | 0% | `int64` | OK |
| `GrupoPaletizacao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `LiberadoProgExped` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (1) |
| `IDPalete` | <span class='manter'>MANTER</span> | 21.4% | 102 | 0.0% | 0.0% | 0% | `float64` | OK |
| `ReferenciaGrupoPaletizacao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `LotePiloto` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.0% | 98.9% | 0% | `int64` | MUITOS ZEROS (98.9%) |
| `Pedido_ERP` | <span class='manter'>MANTER</span> | 12.8% | 128855 | 38.4% | 0% | 0.0% | `object` | OK |
| `Item_ERP` | <span class='manter'>MANTER</span> | 12.8% | 238 | 0.1% | 0% | 0.0% | `object` | OK |
| `Produto_ERP` | <span class='manter'>MANTER</span> | 0.0% | 29053 | 7.6% | 0% | 0.0% | `object` | OK |
| `DataCriacaoRegistro` | <span class='manter'>MANTER</span> | 0.0% | 382129 | 99.4% | 0% | 0% | `datetime64[ns]` | OK |
| `IDUnicoRegistro` | <span class='manter'>MANTER</span> | 0.0% | 384577 | 100.0% | 0% | 0.0% | `object` | OK |
| `ObsAlteracoes` | <span class='excluir'>EXCLUIR</span> | 98.4% | 5777 | 96.1% | 0% | 0.0% | `object` | MUITOS NULOS (98.4%) |
| `IDUsuarioUltModif` | <span class='manter'>MANTER</span> | 5.6% | 116 | 0.0% | 0.0% | 0% | `float64` | OK |
| `UltModificacao` | <span class='manter'>MANTER</span> | 0.0% | 273392 | 71.1% | 0% | 0% | `datetime64[ns]` | OK |
| `Orcamento` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ItemOrcamento` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `CodRepresentante` | <span class='manter'>MANTER</span> | 12.8% | 22 | 0.0% | 0.0% | 0% | `float64` | OK |
| `CodSegmento` | <span class='manter'>MANTER</span> | 48.1% | 20 | 0.0% | 0% | 0.0% | `object` | OK |
| `AreaUtilCedidaFaca` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `AreaBrutaPecaComRefilos` | <span class='manter'>MANTER</span> | 0.0% | 25904 | 6.7% | 0.0% | 0% | `float64` | OK |
| `AreaBrutaPeca` | <span class='manter'>MANTER</span> | 0.0% | 22783 | 5.9% | 0.0% | 0% | `float64` | OK |
| `AreaLiquidaPeca` | <span class='manter'>MANTER</span> | 0.0% | 24434 | 6.4% | 0.0% | 0% | `float64` | OK |
| `AreaBrutaChapa` | <span class='manter'>MANTER</span> | 0.0% | 25781 | 6.7% | 0.0% | 0% | `float64` | OK |
| `AreaLiquidaChapa` | <span class='manter'>MANTER</span> | 0.0% | 22830 | 5.9% | 0.0% | 0% | `float64` | OK |
| `VolumePaleteFechadoM3` | <span class='manter'>MANTER</span> | 21.6% | 4873 | 1.6% | 0.0% | 0% | `float64` | OK |
| `VolumePacoteFechadoM3` | <span class='manter'>MANTER</span> | 21.4% | 6379 | 2.1% | 0.0% | 0% | `float64` | OK |
| `VolumeFechadoPedido` | <span class='manter'>MANTER</span> | 21.5% | 48067 | 15.9% | 0.0% | 0% | `float64` | OK |
| `OrigemPedido` | <span class='manter'>MANTER</span> | 0.0% | 4 | 0.0% | 11.3% | 0% | `int64` | OK |
| `DescOrigemPedido` | <span class='manter'>MANTER</span> | 0.0% | 4 | 0.0% | 0% | 0.0% | `object` | OK |
| `TipoGeracaoPed` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 11.3% | 0% | `int64` | OK |
| `DescTipoGeracaoPed` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.0% | 0% | 0.0% | `object` | OK |
| `idFilialExpedicao` | <span class='excluir'>EXCLUIR</span> | 17.7% | 1 | 0.0% | 0.0% | 0% | `float64` | VALOR ÚNICO (1.0) |
| `QtdImpressoes` | <span class='excluir'>EXCLUIR</span> | 0.0% | 3 | 0.0% | 100.0% | 0% | `int64` | MUITOS ZEROS (100.0%) |
| `DataHoraPrimeiraImpressao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 12 | 10.9% | 0% | 0% | `datetime64[ns]` | MUITOS NULOS (100.0%) |
| `IDUsuarioPrimeiraImpressao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 9 | 8.2% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) |
| `DataHoraUltimaImpressao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 12 | 10.9% | 0% | 0% | `datetime64[ns]` | MUITOS NULOS (100.0%) |
| `IDUsuarioUltimaImpressao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 9 | 8.2% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) |
| `chave_chapa` | <span class='manter'>MANTER</span> | 0.0% | 33312 | 8.7% | 0% | 0.0% | `object` | OK |

---

## Critérios de Exclusão Utilizados

- Muitos Nulos: > 90% de valores nulos
- Valor Único: coluna possui apenas 1 valor único
- Muitos Zeros: > 80% de valores zero (para colunas numéricas)
- Strings Vazias: > 80% de strings vazias (para colunas de texto)

Colunas que não atendem a esses critérios são mantidas.
