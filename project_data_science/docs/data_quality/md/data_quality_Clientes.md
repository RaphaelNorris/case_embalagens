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
- **Tabela:** `dbo.Clientes`
- **Data/Hora:** 2025-09-24 12:51:46
- **Total de Registros:** 899
- **Total de Colunas:** 70
- **Autor:** Raphael Norris - Cientista de Dados

## Filtros Aplicados
- **DataCriacao** >= `2022-01-01`

---

## Query Executada
```sql
SELECT * FROM dbo.Clientes WHERE DataCriacao >= `2022-01-01`
```

---

## Resumo da Análise

| Métrica | Valor |
|---------|-------|
| Total de Colunas | 70 |
| Colunas para Manter | 13 |
| Colunas para Excluir | 57 |
| Percentual de Exclusão | 81.4% |

---

## Colunas Sugeridas para Exclusão

| # | Coluna | Motivos |
|---|--------|---------|
| 1 | `TipoObs1` | STRINGS VAZIAS (89.8%) |
| 2 | `Obs1` | STRINGS VAZIAS (89.8%) |
| 3 | `TipoObs2` | STRINGS VAZIAS (91.5%) |
| 4 | `Obs2` | STRINGS VAZIAS (91.8%) |
| 5 | `TipoObs3` | STRINGS VAZIAS (96.6%) |
| 6 | `Obs3` | STRINGS VAZIAS (96.6%) |
| 7 | `TipoObs4` | STRINGS VAZIAS (98.6%) |
| 8 | `Obs4` | STRINGS VAZIAS (98.6%) |
| 9 | `TipoABC` | MUITOS NULOS (100.0%) |
| 10 | `CodSegmento` | MUITOS NULOS (100.0%) |
| 11 | `PreferencialSN` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| 12 | `ClienteListaSN` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| 13 | `Agrupamento` | MUITOS NULOS (100.0%) |
| 14 | `Cliente_Fornecedor` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 15 | `DescrCliente_Fornecedor` | VALOR ÚNICO (Cliente) |
| 16 | `CodigoERP` | MUITOS NULOS (100.0%) |
| 17 | `Etiqueta` | MUITOS NULOS (99.2%) |
| 18 | `Laudo` | MUITOS NULOS (100.0%) |
| 19 | `EmailLaudo` | MUITOS NULOS (97.4%) |
| 20 | `CartaOrcamento` | MUITOS NULOS (100.0%) |
| 21 | `NrEtiquetas` | MUITOS ZEROS (99.6%) |
| 22 | `idAtendenteVenda` | MUITOS NULOS (100.0%) |
| 23 | `ContatoFaturamento` | MUITOS NULOS (100.0%) |
| 24 | `IDClassFiscal` | MUITOS NULOS (100.0%) |
| 25 | `UsuarioCriacao` | MUITOS NULOS (99.9%) | VALOR ÚNICO (IVAN.ROTTA) |
| 26 | `UsuarioUltModif` | MUITOS NULOS (95.2%) |
| 27 | `RazaoTravaComposicao` | MUITOS NULOS (100.0%) |
| 28 | `CustoFinanceiroAdicional` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 29 | `CustoAdicTransportePorPalete` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 30 | `CustoAdicTransportePorKg_Paletizado` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 31 | `CustoAdicTransportePorKg_NaoPaletizado` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 32 | `CustoAdicTransportePorM2_Paletizado` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 33 | `CustoAdicTransportePorM2_NaoPaletizado` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 34 | `CustoAdicTransportePorPeca_Paletizado` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 35 | `CustoAdicTransportePorPeca_NaoPaletizado` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 36 | `UsoGeralStr1` | MUITOS NULOS (100.0%) |
| 37 | `UsoGeralStr2` | MUITOS NULOS (100.0%) |
| 38 | `UsoGeralNum1` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| 39 | `UsoGeralNum2` | MUITOS NULOS (100.0%) |
| 40 | `ExigeChapaUnitizada` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| 41 | `ExigeAgendamentoEntregas` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| 42 | `ClienteProspecto` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| 43 | `ImprimeLogotipo` | VALOR ÚNICO (True) |
| 44 | `Paletizado` | MUITOS ZEROS (99.9%) |
| 45 | `FacesOpostas` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 46 | `Espelho` | MUITOS ZEROS (99.8%) |
| 47 | `Cantoneiras` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 48 | `Filme` | MUITOS ZEROS (99.9%) |
| 49 | `OrelhasInvertidas` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 50 | `PacotesLargura` | MUITOS NULOS (100.0%) |
| 51 | `PacotesComprimento` | MUITOS NULOS (100.0%) |
| 52 | `PacotesAltura` | MUITOS NULOS (100.0%) |
| 53 | `IDPalete` | MUITOS NULOS (100.0%) |
| 54 | `EmpilhamentoMaximo` | VALOR ÚNICO (1) |
| 55 | `PressaoDeArqueamento` | MUITOS NULOS (100.0%) |
| 56 | `FitasLargPalete` | MUITOS NULOS (100.0%) |
| 57 | `FitasCompPalete` | MUITOS NULOS (100.0%) |

---

## Análise Detalhada de Todas as Colunas

| Coluna | Ação | Nulos (%) | Valores Únicos | Variância (%) | Zeros (%) | Vazias (%) | Tipo | Motivos |
|--------|------|-----------|----------------|---------------|-----------|------------|------|---------|
| `IDCliente` | <span class='manter'>MANTER</span> | 0.0% | 899 | 100.0% | 0.0% | 0% | `int64` | OK |
| `Cliente` | <span class='manter'>MANTER</span> | 0.0% | 887 | 98.7% | 0% | 0.0% | `object` | OK |
| `CodCliente` | <span class='manter'>MANTER</span> | 0.0% | 899 | 100.0% | 0% | 0.0% | `object` | OK |
| `CodRepresentante` | <span class='manter'>MANTER</span> | 0.0% | 20 | 2.2% | 0.0% | 0% | `int64` | OK |
| `TolMais` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.6% | 76.1% | 0% | `int64` | OK |
| `TolMenos` | <span class='manter'>MANTER</span> | 0.0% | 5 | 0.6% | 75.9% | 0% | `int64` | OK |
| `TipoObs1` | <span class='excluir'>EXCLUIR</span> | 0.0% | 7 | 0.8% | 0% | 89.8% | `object` | STRINGS VAZIAS (89.8%) |
| `Obs1` | <span class='excluir'>EXCLUIR</span> | 0.0% | 88 | 9.8% | 0% | 89.8% | `object` | STRINGS VAZIAS (89.8%) |
| `TipoObs2` | <span class='excluir'>EXCLUIR</span> | 0.0% | 6 | 0.7% | 0% | 91.5% | `object` | STRINGS VAZIAS (91.5%) |
| `Obs2` | <span class='excluir'>EXCLUIR</span> | 0.0% | 72 | 8.0% | 0% | 91.8% | `object` | STRINGS VAZIAS (91.8%) |
| `TipoObs3` | <span class='excluir'>EXCLUIR</span> | 0.0% | 5 | 0.6% | 0% | 96.6% | `object` | STRINGS VAZIAS (96.6%) |
| `Obs3` | <span class='excluir'>EXCLUIR</span> | 0.0% | 32 | 3.6% | 0% | 96.6% | `object` | STRINGS VAZIAS (96.6%) |
| `TipoObs4` | <span class='excluir'>EXCLUIR</span> | 0.0% | 7 | 0.8% | 0% | 98.6% | `object` | STRINGS VAZIAS (98.6%) |
| `Obs4` | <span class='excluir'>EXCLUIR</span> | 0.0% | 14 | 1.6% | 0% | 98.6% | `object` | STRINGS VAZIAS (98.6%) |
| `TipoABC` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `CodSegmento` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PreferencialSN` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| `ClienteListaSN` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| `Agrupamento` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Cliente_Fornecedor` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `DescrCliente_Fornecedor` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 0% | 0.0% | `object` | VALOR ÚNICO (Cliente) |
| `RazaoSocial` | <span class='manter'>MANTER</span> | 0.0% | 861 | 95.8% | 0% | 0.0% | `object` | OK |
| `CodigoERP` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Etiqueta` | <span class='excluir'>EXCLUIR</span> | 99.2% | 2 | 28.6% | 0% | 0.0% | `object` | MUITOS NULOS (99.2%) |
| `ExigeLaudo` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.2% | 76.6% | 0% | `bool` | OK |
| `Laudo` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `EmailLaudo` | <span class='excluir'>EXCLUIR</span> | 97.4% | 23 | 100.0% | 0% | 0.0% | `object` | MUITOS NULOS (97.4%) |
| `CartaOrcamento` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `NrEtiquetas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.2% | 99.6% | 0% | `int64` | MUITOS ZEROS (99.6%) |
| `IDUnicoRegistro` | <span class='manter'>MANTER</span> | 0.0% | 899 | 100.0% | 0% | 0.0% | `object` | OK |
| `AceitaPaleteIncompleto` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.2% | 0.0% | 0% | `int64` | OK |
| `DescAceitaPaleteIncompleto` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.2% | 0% | 0.0% | `object` | OK |
| `idAtendenteVenda` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ContatoFaturamento` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `IDClassFiscal` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `DataCriacao` | <span class='manter'>MANTER</span> | 0.0% | 859 | 95.6% | 0% | 0% | `datetime64[ns]` | OK |
| `UsuarioCriacao` | <span class='excluir'>EXCLUIR</span> | 99.9% | 1 | 100.0% | 0% | 0.0% | `object` | MUITOS NULOS (99.9%) | VALOR ÚNICO (IVAN.ROTTA) |
| `DataUltModif` | <span class='manter'>MANTER</span> | 0.0% | 335 | 37.3% | 0% | 0% | `datetime64[ns]` | OK |
| `UsuarioUltModif` | <span class='excluir'>EXCLUIR</span> | 95.2% | 10 | 23.3% | 0% | 0.0% | `object` | MUITOS NULOS (95.2%) |
| `RazaoTravaComposicao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `CustoFinanceiroAdicional` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `CustoAdicTransportePorPalete` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `CustoAdicTransportePorKg_Paletizado` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `CustoAdicTransportePorKg_NaoPaletizado` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `CustoAdicTransportePorM2_Paletizado` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `CustoAdicTransportePorM2_NaoPaletizado` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `CustoAdicTransportePorPeca_Paletizado` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `CustoAdicTransportePorPeca_NaoPaletizado` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `UsoGeralStr1` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `UsoGeralStr2` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `UsoGeralNum1` | <span class='excluir'>EXCLUIR</span> | 84.5% | 1 | 0.7% | 100.0% | 0% | `float64` | VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%) |
| `UsoGeralNum2` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ExigeChapaUnitizada` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| `ExigeAgendamentoEntregas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| `ClienteProspecto` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| `ImprimeLogotipo` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 0.0% | 0% | `bool` | VALOR ÚNICO (True) |
| `Paletizado` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.2% | 99.9% | 0% | `int64` | MUITOS ZEROS (99.9%) |
| `FacesOpostas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `Espelho` | <span class='excluir'>EXCLUIR</span> | 0.0% | 3 | 0.3% | 99.8% | 0% | `int64` | MUITOS ZEROS (99.8%) |
| `Cantoneiras` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `Filme` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.2% | 99.9% | 0% | `int64` | MUITOS ZEROS (99.9%) |
| `OrelhasInvertidas` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `PacotesLargura` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PacotesComprimento` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PacotesAltura` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `IDPalete` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `EmpilhamentoMaximo` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 0.0% | 0% | `int64` | VALOR ÚNICO (1) |
| `PressaoDeArqueamento` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `FitasLargPalete` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `FitasCompPalete` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |

---

## Critérios de Exclusão Utilizados

- Muitos Nulos: > 90% de valores nulos
- Valor Único: coluna possui apenas 1 valor único
- Muitos Zeros: > 80% de valores zero (para colunas numéricas)
- Strings Vazias: > 80% de strings vazias (para colunas de texto)

Colunas que não atendem a esses critérios são mantidas.
