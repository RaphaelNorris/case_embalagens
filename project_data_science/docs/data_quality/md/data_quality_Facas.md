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
- **Tabela:** `dbo.Facas`
- **Data/Hora:** 2025-09-24 12:55:37
- **Total de Registros:** 8139
- **Total de Colunas:** 21
- **Autor:** Raphael Norris

---

## Filtros Aplicados
- **DataCriacaoRegistro** >= `2022-01-01`

---

## Query Executada
```sql
SELECT * FROM dbo.Facas WHERE DataCriacaoRegistro >= `2022-01-01`
```


---

## Resumo da Análise

| Métrica | Valor |
|---------|-------|
| Total de Colunas | 21 |
| Colunas para Manter | 15 |
| Colunas para Excluir | 6 |
| Percentual de Exclusão | 28.6% |

---

## Colunas Sugeridas para Exclusão

| # | Coluna | Motivos |
|---|--------|---------|
| 1 | `Largura` | MUITOS NULOS (100.0%) |
| 2 | `Comprimento` | MUITOS NULOS (100.0%) |
| 3 | `Localizacao` | MUITOS NULOS (97.5%) |
| 4 | `CodigoERP` | MUITOS NULOS (100.0%) |
| 5 | `ChaveEstadoFerramenta` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 6 | `RefugoCliente` | MUITOS NULOS (100.0%) | VALOR ÚNICO (8.27) |

---

## Análise Detalhada de Todas as Colunas

| Coluna | Ação | Nulos (%) | Valores Únicos | Variância (%) | Zeros (%) | Vazias (%) | Tipo | Motivos |
|--------|------|-----------|----------------|---------------|-----------|------------|------|---------|
| `CodFaca` | <span class='manter'>MANTER</span> | 0.0% | 8139 | 100.0% | 0% | 0.0% | `object` | OK |
| `Tipo` | <span class='manter'>MANTER</span> | 15.5% | 2 | 0.0% | 0.0% | 0% | `float64` | OK |
| `DescrTipoFaca` | <span class='manter'>MANTER</span> | 0.0% | 3 | 0.0% | 0% | 15.5% | `object` | OK |
| `Fornecedor` | <span class='manter'>MANTER</span> | 23.4% | 29 | 0.5% | 0% | 2.2% | `object` | OK |
| `Modulo` | <span class='manter'>MANTER</span> | 18.9% | 61 | 0.9% | 0% | 0.1% | `object` | OK |
| `Arquivo` | <span class='manter'>MANTER</span> | 83.1% | 1086 | 79.0% | 0% | 7.1% | `object` | OK |
| `Largura` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Comprimento` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `PecasPorFaca` | <span class='manter'>MANTER</span> | 0.0% | 17 | 0.2% | 0.0% | 0% | `int64` | OK |
| `Localizacao` | <span class='excluir'>EXCLUIR</span> | 97.5% | 51 | 24.9% | 0% | 5.9% | `object` | MUITOS NULOS (97.5%) |
| `Figura` | <span class='manter'>MANTER</span> | 0.0% | 8103 | 99.6% | 0% | 0.0% | `object` | OK |
| `Status` | <span class='manter'>MANTER</span> | 3.4% | 5 | 0.1% | 0.0% | 0% | `float64` | OK |
| `Preco` | <span class='manter'>MANTER</span> | 27.0% | 4458 | 75.0% | 0.0% | 0% | `float64` | OK |
| `CompLamina` | <span class='manter'>MANTER</span> | 70.6% | 1995 | 83.4% | 0.0% | 0% | `float64` | OK |
| `IDCliente` | <span class='manter'>MANTER</span> | 39.4% | 962 | 19.5% | 0.0% | 0% | `float64` | OK |
| `Obs` | <span class='manter'>MANTER</span> | 90.0% | 450 | 55.3% | 0% | 0.4% | `object` | OK |
| `CodigoERP` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ChaveEstadoFerramenta` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `DesativadoSN` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 26.0% | 0% | `bool` | OK |
| `RefugoCliente` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 100.0% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) | VALOR ÚNICO (8.27) |
| `DataCriacaoRegistro` | <span class='manter'>MANTER</span> | 0.0% | 1152 | 14.2% | 0% | 0% | `datetime64[ns]` | OK |

---

## Critérios de Exclusão Utilizados

- Muitos Nulos: > 90% de valores nulos
- Valor Único: coluna possui apenas 1 valor único
- Muitos Zeros: > 80% de valores zero (para colunas numéricas)
- Strings Vazias: > 80% de strings vazias (para colunas de texto)

Colunas que não atendem a esses critérios são mantidas.
