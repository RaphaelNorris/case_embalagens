CREATE TABLE PARADAS (
    IDPARADA                     NUMBER         NOT NULL,
    PARADA                       NUMBER         NOT NULL,
    DESCRICAO                    VARCHAR2(30)   NULL,
    SETOR                        VARCHAR2(30)   NULL,
    TIPO                         NUMBER         NULL,
    CODIGOERP                    VARCHAR2(30)   NULL,
    MODOVALIDACAO                NUMBER         NOT NULL,
    TEXTOVALIDACAO               VARCHAR2(255)  NULL,
    USADAONDULADEIRA             CHAR(1)        NOT NULL, -- bit
    USADACONVERSAO               CHAR(1)        NOT NULL, -- bit
    DESATIVADA                   CHAR(1)        NOT NULL, -- bit
    FLAGAJUSTE                   CHAR(1)        NOT NULL, -- bit
    FLAGEXTERNA                  CHAR(1)        NOT NULL, -- bit
    FLAGCONTINUACAOAJUSTE        CHAR(1)        NOT NULL, -- bit
    FLAGASSOCIADOAOPRODUTO       CHAR(1)        NOT NULL, -- bit
    FORCATROCACONVERSAOONLINE    CHAR(1)        NOT NULL, -- bit
    EXCLUIOEE                    CHAR(1)        NOT NULL, -- bit
    EXIGEINFORMACAOSECAOMAQCONV  CHAR(1)        NOT NULL, -- bit,
    CONSTRAINT PK_PARADAS PRIMARY KEY (IDPARADA)
)
