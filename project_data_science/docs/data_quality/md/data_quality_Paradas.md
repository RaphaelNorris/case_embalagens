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
- **Tabela:** `dbo.Paradas`
- **Data/Hora:** 2025-09-24 13:33:49
- **Total de Registros:** 699
- **Total de Colunas:** 18
- **Autor:** Raphael Norris

---

## Filtros Aplicados
- Nenhum filtro aplicado

---

## Query Executada
```sql
SELECT * FROM dbo.Paradas
```

---

## Resumo da Análise

| Métrica | Valor |
|---------|-------|
| Total de Colunas | 18 |
| Colunas para Manter | 6 |
| Colunas para Excluir | 12 |
| Percentual de Exclusão | 66.7% |

---

## Colunas Sugeridas para Exclusão

| # | Coluna | Motivos |
|---|--------|---------|
| 1 | `CodigoERP` | MUITOS NULOS (99.9%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| 2 | `ModoValidacao` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| 3 | `TextoValidacao` | MUITOS NULOS (100.0%) |
| 4 | `UsadaConversao` | MUITOS ZEROS (93.1%) |
| 5 | `Desativada` | MUITOS ZEROS (98.1%) |
| 6 | `flagAjuste` | MUITOS ZEROS (99.9%) |
| 7 | `flagExterna` | MUITOS ZEROS (96.9%) |
| 8 | `FlagContinuacaoAjuste` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| 9 | `FlagAssociadoAoProduto` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| 10 | `ForcaTrocaConversaoOnline` | MUITOS ZEROS (99.9%) |
| 11 | `ExcluiOEE` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| 12 | `ExigeInformacaoSecaoMaqConv` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |

---

## Análise Detalhada de Todas as Colunas

| Coluna | Ação | Nulos (%) | Valores Únicos | Variância (%) | Zeros (%) | Vazias (%) | Tipo | Motivos |
|--------|------|-----------|----------------|---------------|-----------|------------|------|---------|
| `idParada` | <span class='manter'>MANTER</span> | 0.0% | 699 | 100.0% | 0.0% | 0% | `int64` | OK |
| `Parada` | <span class='manter'>MANTER</span> | 0.0% | 699 | 100.0% | 0.0% | 0% | `int64` | OK |
| `Descricao` | <span class='manter'>MANTER</span> | 10.0% | 238 | 37.8% | 0% | 0.2% | `object` | OK |
| `Setor` | <span class='manter'>MANTER</span> | 6.4% | 20 | 3.1% | 0% | 0.0% | `object` | OK |
| `Tipo` | <span class='manter'>MANTER</span> | 12.3% | 65 | 10.6% | 0.0% | 0% | `float64` | OK |
| `CodigoERP` | <span class='excluir'>EXCLUIR</span> | 99.9% | 1 | 100.0% | 0% | 100.0% | `object` | MUITOS NULOS (99.9%) | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| `ModoValidacao` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `int64` | VALOR ÚNICO (0) | MUITOS ZEROS (100.0%) |
| `TextoValidacao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `UsadaOnduladeira` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.3% | 6.9% | 0% | `bool` | OK |
| `UsadaConversao` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.3% | 93.1% | 0% | `bool` | MUITOS ZEROS (93.1%) |
| `Desativada` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.3% | 98.1% | 0% | `bool` | MUITOS ZEROS (98.1%) |
| `flagAjuste` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.3% | 99.9% | 0% | `bool` | MUITOS ZEROS (99.9%) |
| `flagExterna` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.3% | 96.9% | 0% | `bool` | MUITOS ZEROS (96.9%) |
| `FlagContinuacaoAjuste` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| `FlagAssociadoAoProduto` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| `ForcaTrocaConversaoOnline` | <span class='excluir'>EXCLUIR</span> | 0.0% | 2 | 0.3% | 99.9% | 0% | `bool` | MUITOS ZEROS (99.9%) |
| `ExcluiOEE` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |
| `ExigeInformacaoSecaoMaqConv` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.1% | 100.0% | 0% | `bool` | VALOR ÚNICO (False) | MUITOS ZEROS (100.0%) |

---

## Critérios de Exclusão Utilizados

- Muitos Nulos: > 90% de valores nulos
- Valor Único: coluna possui apenas 1 valor único
- Muitos Zeros: > 80% de valores zero (para colunas numéricas)
- Strings Vazias: > 80% de strings vazias (para colunas de texto)

Colunas que não atendem a esses critérios são mantidas.
