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
- **Tabela:** `dbo.FI`
- **Data/Hora:** 2025-09-24 13:33:49
- **Total de Registros:** 24140
- **Total de Colunas:** 27
- **Autor:** Raphael Norris

---

## Filtros Aplicados
- Nenhum filtro aplicado

---

## Query Executada
```sql
SELECT * FROM dbo.FI
```

---

## Resumo da Análise

| Métrica | Valor |
|---------|-------|
| Total de Colunas | 27 |
| Colunas para Manter | 10 |
| Colunas para Excluir | 17 |
| Percentual de Exclusão | 63.0% |

---

## Colunas Sugeridas para Exclusão

| # | Coluna | Motivos |
|---|--------|---------|
| 1 | `Localizacao` | MUITOS NULOS (100.0%) | STRINGS VAZIAS (100.0%) |
| 2 | `Status` | MUITOS NULOS (100.0%) |
| 3 | `FacesImpressas` | MUITOS NULOS (100.0%) |
| 4 | `AbasImpressas` | MUITOS NULOS (100.0%) |
| 5 | `Obs` | MUITOS NULOS (98.8%) |
| 6 | `DescrStatusFI` | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| 7 | `ConsumoCor1` | MUITOS NULOS (90.8%) |
| 8 | `ViscosidadeCor1` | MUITOS NULOS (100.0%) | VALOR ÚNICO (24.0) |
| 9 | `ViscosidadeCor2` | MUITOS NULOS (100.0%) | VALOR ÚNICO (26.0) |
| 10 | `ViscosidadeCor3` | MUITOS NULOS (100.0%) | VALOR ÚNICO (23.0) |
| 11 | `ViscosidadeCor4` | MUITOS NULOS (100.0%) | VALOR ÚNICO (104.0) |
| 12 | `Cor5` | MUITOS NULOS (97.2%) | STRINGS VAZIAS (98.8%) |
| 13 | `ConsumoCor5` | MUITOS NULOS (100.0%) |
| 14 | `ViscosidadeCor5` | MUITOS NULOS (100.0%) |
| 15 | `Cor6` | MUITOS NULOS (96.3%) |
| 16 | `ConsumoCor6` | MUITOS NULOS (100.0%) |
| 17 | `ViscosidadeCor6` | MUITOS NULOS (100.0%) |

---

## Análise Detalhada de Todas as Colunas

| Coluna | Ação | Nulos (%) | Valores Únicos | Variância (%) | Zeros (%) | Vazias (%) | Tipo | Motivos |
|--------|------|-----------|----------------|---------------|-----------|------------|------|---------|
| `CodFI` | <span class='manter'>MANTER</span> | 0.0% | 24140 | 100.0% | 0% | 0.0% | `object` | OK |
| `Localizacao` | <span class='excluir'>EXCLUIR</span> | 100.0% | 2 | 22.2% | 0% | 100.0% | `object` | MUITOS NULOS (100.0%) | STRINGS VAZIAS (100.0%) |
| `Figura` | <span class='manter'>MANTER</span> | 5.7% | 15806 | 69.5% | 0% | 0.0% | `object` | OK |
| `Status` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `FacesImpressas` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `AbasImpressas` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Obs` | <span class='excluir'>EXCLUIR</span> | 98.8% | 180 | 61.9% | 0% | 1.7% | `object` | MUITOS NULOS (98.8%) |
| `DescrStatusFI` | <span class='excluir'>EXCLUIR</span> | 0.0% | 1 | 0.0% | 0% | 100.0% | `object` | VALOR ÚNICO () | STRINGS VAZIAS (100.0%) |
| `DesativadoSN` | <span class='manter'>MANTER</span> | 0.0% | 2 | 0.0% | 39.2% | 0% | `bool` | OK |
| `Cor1` | <span class='manter'>MANTER</span> | 19.0% | 149 | 0.8% | 0% | 36.8% | `object` | OK |
| `ConsumoCor1` | <span class='excluir'>EXCLUIR</span> | 90.8% | 940 | 42.3% | 0.0% | 0% | `float64` | MUITOS NULOS (90.8%) |
| `ViscosidadeCor1` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 100.0% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) | VALOR ÚNICO (24.0) |
| `Cor2` | <span class='manter'>MANTER</span> | 21.6% | 156 | 0.8% | 0% | 36.4% | `object` | OK |
| `ConsumoCor2` | <span class='manter'>MANTER</span> | 85.1% | 1487 | 41.4% | 0.0% | 0% | `float64` | OK |
| `ViscosidadeCor2` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 100.0% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) | VALOR ÚNICO (26.0) |
| `Cor3` | <span class='manter'>MANTER</span> | 29.8% | 154 | 0.9% | 0% | 46.8% | `object` | OK |
| `ConsumoCor3` | <span class='manter'>MANTER</span> | 83.2% | 1330 | 32.8% | 0.0% | 0% | `float64` | OK |
| `ViscosidadeCor3` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 50.0% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) | VALOR ÚNICO (23.0) |
| `Cor4` | <span class='manter'>MANTER</span> | 27.6% | 84 | 0.5% | 0% | 46.2% | `object` | OK |
| `ConsumoCor4` | <span class='manter'>MANTER</span> | 81.2% | 1363 | 30.0% | 0.1% | 0% | `float64` | OK |
| `ViscosidadeCor4` | <span class='excluir'>EXCLUIR</span> | 100.0% | 1 | 50.0% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) | VALOR ÚNICO (104.0) |
| `Cor5` | <span class='excluir'>EXCLUIR</span> | 97.2% | 2 | 0.3% | 0% | 98.8% | `object` | MUITOS NULOS (97.2%) | STRINGS VAZIAS (98.8%) |
| `ConsumoCor5` | <span class='excluir'>EXCLUIR</span> | 100.0% | 5 | 71.4% | 0.0% | 0% | `float64` | MUITOS NULOS (100.0%) |
| `ViscosidadeCor5` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `Cor6` | <span class='excluir'>EXCLUIR</span> | 96.3% | 2 | 0.2% | 0% | 73.3% | `object` | MUITOS NULOS (96.3%) |
| `ConsumoCor6` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |
| `ViscosidadeCor6` | <span class='excluir'>EXCLUIR</span> | 100.0% | 0 | 0% | 0% | 0% | `object` | MUITOS NULOS (100.0%) |

---

## Critérios de Exclusão Utilizados

- Muitos Nulos: > 90% de valores nulos
- Valor Único: coluna possui apenas 1 valor único
- Muitos Zeros: > 80% de valores zero (para colunas numéricas)
- Strings Vazias: > 80% de strings vazias (para colunas de texto)

Colunas que não atendem a esses critérios são mantidas.
