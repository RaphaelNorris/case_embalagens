CREATE TABLE CLICHES (
    CODCLICHE             VARCHAR2(30)    NOT NULL,
    TIPO                  NUMBER          NOT NULL,
    DESCRTIPOCLICHE       VARCHAR2(30)    NULL,
    FORNECEDOR            VARCHAR2(25)    NULL,
    MODULO                VARCHAR2(50)    NULL,
    ARQUIVO               VARCHAR2(50)    NULL,
    LOCALIZACAO           VARCHAR2(50)    NULL,
    FIGURA                VARCHAR2(99)    NULL,
    STATUS                NUMBER          NULL,
    PRECO                 BINARY_DOUBLE   NULL,
    AREA                  NUMBER          NULL,
    IDCLIENTE             NUMBER          NULL,
    OBS                   VARCHAR2(1000)  NULL,
    CODIGOERP             VARCHAR2(30)    NULL,
    CHAVEESTADOFERRAMENTA NUMBER          NOT NULL,
    DESATIVADOSN          CHAR(1)         NOT NULL, -- bit
    DATACRIACAOREGISTRO   DATE            NULL,
    CONSTRAINT PK_CLICHES PRIMARY KEY (CODCLICHE)
)
