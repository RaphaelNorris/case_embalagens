CREATE TABLE PARADAS (
    IDPARADA                     NUMBER         NOT NULL,
    PARADA                       NUMBER         NOT NULL,
    DESCRICAO                    VARCHAR2(30)   NULL,
    SETOR                        VARCHAR2(30)   NULL,
    TIPO                         NUMBER         NULL,
    USADAONDULADEIRA             CHAR(1)        NOT NULL, -- bit
	USADACONVERSAO               CHAR(1)        NOT NULL, -- bit
    DESATIVADA                   CHAR(1)        NOT NULL, -- bit
    FLAGAJUSTE                   CHAR(1)        NOT NULL, -- bit
    FLAGEXTERNA                  CHAR(1)        NOT NULL, -- bit
    CONSTRAINT PK_PARADAS PRIMARY KEY (IDPARADA)
)




