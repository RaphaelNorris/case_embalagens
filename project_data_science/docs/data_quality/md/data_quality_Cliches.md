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
- **Tabela:** `dbo.Cliches`
- **Data/Hora:** 2025-09-24 13:16:23
- **Total de Registros:** 16786
- **Total de Colunas:** 17
- **Autor:** Raphael Norris

---

## Filtros Aplicados
- **DataCriacaoRegistro** >= `2022-01-01`

---

## Query Executada
```sql
SELECT * FROM dbo.Cliches WHERE DataCriacaoRegistro >= `2022-01-01`
```


---

## Resumo da Análise

| Métrica | Valor |
|---------|-------|
| Total de Colunas | 17 |
| Colunas para Manter | 9 |
| Colunas para Excluir | 8 |
| Percentual de Exclusão | 47.1% |

---

## Colunas Sugeridas para Exclusão

| # | Coluna | Motivos |
|---|--------|---------|
| 1 | `Tipo` | VALOR ÚNICO (1) |
| 2 | `DescrTipoCliche` | VALOR ÚNICO (Cyrel) |
| 3 | `Arquivo` | MUITOS NULOS (99.5%) |
| 4 | `Localizacao` | MUITOS NULOS (100.0%) | STRINGS VAZIAS (87.5%) |
| 5 | `Area` | MUITOS NULOS (100.0%) |
| 6 | `Obs` | MUITOS NULOS (98.3%) |
| 7 | `CodigoERP` | MUITOS NULOS (100.0%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| 8 | `ChaveEstadoFerramenta` | VALOR ÚNICO (1) |

---

## Análise Detalhada de Todas as Colunas

| Coluna | Ação | Nulos (%) | Valores Únicos | Variância (%) | Zeros (%) | Vazias (%) | Tipo | Motivos |
|--------|------|-----------|----------------|---------------|-----------|------------|------|---------|
| `CodCliche` | <span class='manter'>MANTER</span> | 0.0% | 16786 | 100.0% | 0% | 0.0% | `object` | OK |
| `Tipo` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (1) |
| `DescrTipoCliche` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 0% | 0.0% | `object` | VALOR ÚNICO (Cyrel) |
| `Fornecedor` | <span class='manter'>MANTER</span> | 26.2% | 69 | 0.6% | 0% | 0.2% | `object` | OK |
| `Modulo` | <span class='manter'>MANTER</span> | 51.3% | 56 | 0.7% | 0% | 0.1% | `object` | OK |
| `Arquivo` | <span class='excluir'>EXCLUIR</span> | 99.5% | 25 | 27.8% | 0% | 72.2% | `object` | MUITOS NULOS (99.5%) |
| `Localizacao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 3 | 37.5% | 0% | 87.5% | `object` | MUITOS NULOS (100.0%) | STRINGS VAZIAS (87.5%) |
| `Figura` | <span class='manter'>MANTER</span> | 0.0% | 16777 | 100.0% | 0% | 0.0% | `object` | OK |
| `Status` | <span class='manter'>MANTER</span> | 12.4% | 5 | 0.0% | 0.0% | 0% | `float64` | OK |
| `Preco` | <span class='manter'>MANTER</span> | 28.5% | 10642 | 88.7% | 0.0% | 0% | `float64` | OK |
| `Area` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `IDCliente` | <span class='manter'>MANTER</span> | 43.1% | 1388 | 14.5% | 0.0% | 0% | `float64` | OK |
| `Obs` | <span class='excluir'>EXCLUIR</span> | 98.3% | 182 | 62.5% | 0% | 1.0% | `object` | MUITOS NULOS (98.3%) |
| `CodigoERP` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 33.3% | 0% | 100.0% | `object` | MUITOS NULOS (100.0%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| `ChaveEstadoFerramenta` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 0.0% | 0% | `int64` | VALOR ÚNICO (1) |
| `DesativadoSN` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 58.5% | 0% | `bool` | OK |
| `DataCriacaoRegistro` | <span class='manter'>MANTER</span> | 0.0% | 1937 | 11.5% | 0% | 0% | `datetime64[ns]` | OK |

---

## Critérios de Exclusão Utilizados

- Muitos Nulos: > 90% de valores nulos
- Valor Único: coluna possui apenas 1 valor único
- Muitos Zeros: > 80% de valores zero (para colunas numéricas)
- Strings Vazias: > 80% de strings vazias (para colunas de texto)

Colunas que não atendem a esses critérios são mantidas.
