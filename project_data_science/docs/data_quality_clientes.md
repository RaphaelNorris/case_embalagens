
IDENTIFICANDO COLUNAS PARA EXCLUSÃO
Tabela: dbo.Clientes
Filtros aplicados:
  - DataCriacao >= 2022-01-01
Critérios: Nulos >90%, Variância <0.1%, Zeros >80%
======================================================================
Query executada: SELECT * FROM dbo.Clientes WHERE DataCriacao >= ?
Parâmetros: ('2022-01-01',)
Tentando pymssql...
pymssql falhou: module 'pymssql' has no attribute 'connect'
Tentando pyodbc com ODBC Driver 17 for SQL Server...
SUCESSO: Conectado via pyodbc + ODBC Driver 17 for SQL Server
Analisando 892 registros, 70 colunas

ANALISE DETALHADA DE TODAS AS COLUNAS:
----------------------------------------------------------------------
IDCliente                 MANTER   - 892 únicos (100.0%), 0.0% nulos
Cliente                   MANTER   - 880 únicos (98.7%), 0.0% nulos
CodCliente                MANTER   - 892 únicos (100.0%), 0.0% nulos
CodRepresentante          MANTER   - 20 únicos (2.2%), 0.0% nulos
TolMais                   MANTER   - 5 únicos (0.6%), 0.0% nulos, 75.9% zeros
TolMenos                  MANTER   - 5 únicos (0.6%), 0.0% nulos, 75.7% zeros
TipoObs1                  EXCLUIR  - STRINGS VAZIAS (89.7%)
Obs1                      EXCLUIR  - STRINGS VAZIAS (89.7%)
TipoObs2                  EXCLUIR  - STRINGS VAZIAS (91.5%)
Obs2                      EXCLUIR  - STRINGS VAZIAS (91.7%)
TipoObs3                  EXCLUIR  - STRINGS VAZIAS (96.5%)
Obs3                      EXCLUIR  - STRINGS VAZIAS (96.5%)
TipoObs4                  EXCLUIR  - STRINGS VAZIAS (98.5%)
Obs4                      EXCLUIR  - STRINGS VAZIAS (98.5%)
TipoABC                   EXCLUIR  - MUITOS NULOS (100.0%)
CodSegmento               EXCLUIR  - MUITOS NULOS (100.0%)
PreferencialSN            EXCLUIR  - VALOR ÚNICO (False) | MUITOS ZEROS (100.0%)
ClienteListaSN            EXCLUIR  - VALOR ÚNICO (False) | MUITOS ZEROS (100.0%)
Agrupamento               EXCLUIR  - MUITOS NULOS (100.0%)
Cliente_Fornecedor        EXCLUIR  - VALOR ÚNICO (0) | MUITOS ZEROS (100.0%)
DescrCliente_Fornecedor   EXCLUIR  - VALOR ÚNICO (Cliente)
RazaoSocial               MANTER   - 854 únicos (95.7%), 0.0% nulos
CodigoERP                 EXCLUIR  - MUITOS NULOS (100.0%)
Etiqueta                  EXCLUIR  - MUITOS NULOS (99.2%)
ExigeLaudo                MANTER   - 2 únicos (0.2%), 0.0% nulos, 76.5% zeros
Laudo                     EXCLUIR  - MUITOS NULOS (100.0%)
EmailLaudo                EXCLUIR  - MUITOS NULOS (97.4%)
CartaOrcamento            EXCLUIR  - MUITOS NULOS (100.0%)
NrEtiquetas               EXCLUIR  - MUITOS ZEROS (99.6%)
IDUnicoRegistro           MANTER   - 892 únicos (100.0%), 0.0% nulos
AceitaPaleteIncompleto    MANTER   - 2 únicos (0.2%), 0.0% nulos
DescAceitaPaleteIncompleto MANTER   - 2 únicos (0.2%), 0.0% nulos
idAtendenteVenda          EXCLUIR  - MUITOS NULOS (100.0%)
ContatoFaturamento        EXCLUIR  - MUITOS NULOS (100.0%)
IDClassFiscal             EXCLUIR  - MUITOS NULOS (100.0%)
DataCriacao               MANTER   - 852 únicos (95.5%), 0.0% nulos
UsuarioCriacao            EXCLUIR  - MUITOS NULOS (99.9%) | VALOR ÚNICO (IVAN.ROTTA)
DataUltModif              MANTER   - 328 únicos (36.8%), 0.0% nulos
UsuarioUltModif           EXCLUIR  - MUITOS NULOS (95.2%)
RazaoTravaComposicao      EXCLUIR  - MUITOS NULOS (100.0%)
CustoFinanceiroAdicional  EXCLUIR  - VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
CustoAdicTransportePorPalete EXCLUIR  - VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
CustoAdicTransportePorKg_Paletizado EXCLUIR  - VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
CustoAdicTransportePorKg_NaoPaletizado EXCLUIR  - VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
CustoAdicTransportePorM2_Paletizado EXCLUIR  - VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
CustoAdicTransportePorM2_NaoPaletizado EXCLUIR  - VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
CustoAdicTransportePorPeca_Paletizado EXCLUIR  - VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
CustoAdicTransportePorPeca_NaoPaletizado EXCLUIR  - VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
UsoGeralStr1              EXCLUIR  - MUITOS NULOS (100.0%)
UsoGeralStr2              EXCLUIR  - MUITOS NULOS (100.0%)
UsoGeralNum1              EXCLUIR  - VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
UsoGeralNum2              EXCLUIR  - MUITOS NULOS (100.0%)
ExigeChapaUnitizada       EXCLUIR  - VALOR ÚNICO (False) | MUITOS ZEROS (100.0%)
ExigeAgendamentoEntregas  EXCLUIR  - VALOR ÚNICO (False) | MUITOS ZEROS (100.0%)
ClienteProspecto          EXCLUIR  - VALOR ÚNICO (False) | MUITOS ZEROS (100.0%)
ImprimeLogotipo           EXCLUIR  - VALOR ÚNICO (True)
Paletizado                EXCLUIR  - MUITOS ZEROS (99.9%)
FacesOpostas              EXCLUIR  - VALOR ÚNICO (0) | MUITOS ZEROS (100.0%)
Espelho                   EXCLUIR  - MUITOS ZEROS (99.8%)
Cantoneiras               EXCLUIR  - VALOR ÚNICO (0) | MUITOS ZEROS (100.0%)
Filme                     EXCLUIR  - MUITOS ZEROS (99.9%)
OrelhasInvertidas         EXCLUIR  - VALOR ÚNICO (0) | MUITOS ZEROS (100.0%)
PacotesLargura            EXCLUIR  - MUITOS NULOS (100.0%)
PacotesComprimento        EXCLUIR  - MUITOS NULOS (100.0%)
PacotesAltura             EXCLUIR  - MUITOS NULOS (100.0%)
IDPalete                  EXCLUIR  - MUITOS NULOS (100.0%)
EmpilhamentoMaximo        EXCLUIR  - VALOR ÚNICO (1)
PressaoDeArqueamento      EXCLUIR  - MUITOS NULOS (100.0%)
FitasLargPalete           EXCLUIR  - MUITOS NULOS (100.0%)
FitasCompPalete           EXCLUIR  - MUITOS NULOS (100.0%)

RESUMO DA ANÁLISE:
--------------------------------------------------
Total de colunas analisadas: 70
Colunas para MANTER: 13
Colunas para EXCLUIR: 57

LISTA COMPLETA DE EXCLUSÃO:
----------------------------------------
 1. TipoObs1 → STRINGS VAZIAS (89.7%)
 2. Obs1 → STRINGS VAZIAS (89.7%)
 3. TipoObs2 → STRINGS VAZIAS (91.5%)
 4. Obs2 → STRINGS VAZIAS (91.7%)
 5. TipoObs3 → STRINGS VAZIAS (96.5%)
 6. Obs3 → STRINGS VAZIAS (96.5%)
 7. TipoObs4 → STRINGS VAZIAS (98.5%)
 8. Obs4 → STRINGS VAZIAS (98.5%)
 9. TipoABC → MUITOS NULOS (100.0%)
10. CodSegmento → MUITOS NULOS (100.0%)
11. PreferencialSN → VALOR ÚNICO (False) | MUITOS ZEROS (100.0%)
12. ClienteListaSN → VALOR ÚNICO (False) | MUITOS ZEROS (100.0%)
13. Agrupamento → MUITOS NULOS (100.0%)
14. Cliente_Fornecedor → VALOR ÚNICO (0) | MUITOS ZEROS (100.0%)
15. DescrCliente_Fornecedor → VALOR ÚNICO (Cliente)
16. CodigoERP → MUITOS NULOS (100.0%)
17. Etiqueta → MUITOS NULOS (99.2%)
18. Laudo → MUITOS NULOS (100.0%)
19. EmailLaudo → MUITOS NULOS (97.4%)
20. CartaOrcamento → MUITOS NULOS (100.0%)
21. NrEtiquetas → MUITOS ZEROS (99.6%)
22. idAtendenteVenda → MUITOS NULOS (100.0%)
23. ContatoFaturamento → MUITOS NULOS (100.0%)
24. IDClassFiscal → MUITOS NULOS (100.0%)
25. UsuarioCriacao → MUITOS NULOS (99.9%) | VALOR ÚNICO (IVAN.ROTTA)
26. UsuarioUltModif → MUITOS NULOS (95.2%)
27. RazaoTravaComposicao → MUITOS NULOS (100.0%)
28. CustoFinanceiroAdicional → VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
29. CustoAdicTransportePorPalete → VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
30. CustoAdicTransportePorKg_Paletizado → VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
31. CustoAdicTransportePorKg_NaoPaletizado → VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
32. CustoAdicTransportePorM2_Paletizado → VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
33. CustoAdicTransportePorM2_NaoPaletizado → VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
34. CustoAdicTransportePorPeca_Paletizado → VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
35. CustoAdicTransportePorPeca_NaoPaletizado → VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
36. UsoGeralStr1 → MUITOS NULOS (100.0%)
37. UsoGeralStr2 → MUITOS NULOS (100.0%)
38. UsoGeralNum1 → VALOR ÚNICO (0.0) | MUITOS ZEROS (100.0%)
39. UsoGeralNum2 → MUITOS NULOS (100.0%)
40. ExigeChapaUnitizada → VALOR ÚNICO (False) | MUITOS ZEROS (100.0%)
41. ExigeAgendamentoEntregas → VALOR ÚNICO (False) | MUITOS ZEROS (100.0%)
42. ClienteProspecto → VALOR ÚNICO (False) | MUITOS ZEROS (100.0%)
43. ImprimeLogotipo → VALOR ÚNICO (True)
44. Paletizado → MUITOS ZEROS (99.9%)
45. FacesOpostas → VALOR ÚNICO (0) | MUITOS ZEROS (100.0%)
46. Espelho → MUITOS ZEROS (99.8%)
47. Cantoneiras → VALOR ÚNICO (0) | MUITOS ZEROS (100.0%)
48. Filme → MUITOS ZEROS (99.9%)
49. OrelhasInvertidas → VALOR ÚNICO (0) | MUITOS ZEROS (100.0%)
50. PacotesLargura → MUITOS NULOS (100.0%)
51. PacotesComprimento → MUITOS NULOS (100.0%)
52. PacotesAltura → MUITOS NULOS (100.0%)
53. IDPalete → MUITOS NULOS (100.0%)
54. EmpilhamentoMaximo → VALOR ÚNICO (1)
55. PressaoDeArqueamento → MUITOS NULOS (100.0%)
56. FitasLargPalete → MUITOS NULOS (100.0%)
57. FitasCompPalete → MUITOS NULOS (100.0%)

COMANDO SQL PARA EXCLUSÃO:
----------------------------------------
-- Excluir 57 colunas da tabela dbo.Clientes
ALTER TABLE dbo.Clientes
DROP COLUMN TipoObs1, Obs1, TipoObs2, Obs2, TipoObs3, Obs3, TipoObs4, Obs4, TipoABC, CodSegmento, PreferencialSN, ClienteListaSN, Agrupamento, Cliente_Fornecedor, DescrCliente_Fornecedor, CodigoERP, Etiqueta, Laudo, EmailLaudo, CartaOrcamento, NrEtiquetas, idAtendenteVenda, ContatoFaturamento, IDClassFiscal, UsuarioCriacao, UsuarioUltModif, RazaoTravaComposicao, CustoFinanceiroAdicional, CustoAdicTransportePorPalete, CustoAdicTransportePorKg_Paletizado, CustoAdicTransportePorKg_NaoPaletizado, CustoAdicTransportePorM2_Paletizado, CustoAdicTransportePorM2_NaoPaletizado, CustoAdicTransportePorPeca_Paletizado, CustoAdicTransportePorPeca_NaoPaletizado, UsoGeralStr1, UsoGeralStr2, UsoGeralNum1, UsoGeralNum2, ExigeChapaUnitizada, ExigeAgendamentoEntregas, ClienteProspecto, ImprimeLogotipo, Paletizado, FacesOpostas, Espelho, Cantoneiras, Filme, OrelhasInvertidas, PacotesLargura, PacotesComprimento, PacotesAltura, IDPalete, EmpilhamentoMaximo, PressaoDeArqueamento, FitasLargPalete, FitasCompPalete;

-- Ou criar nova tabela apenas com colunas úteis:
SELECT IDCliente, Cliente, CodCliente, CodRepresentante, TolMais, TolMenos, RazaoSocial, ExigeLaudo, IDUnicoRegistro, AceitaPaleteIncompleto, DescAceitaPaleteIncompleto, DataCriacao, DataUltModif
INTO dbo.Clientes_cleaned
FROM dbo.Clientes
WHERE DataCriacao >= '2022-01-01'
;
Erro ao salvar Excel: No module named 'openpyxl'
Relatório CSV salvo: data_quality_Clientes_20250924_092350.csv
