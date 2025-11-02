CREATE TABLE CLICHES (
    CODCLICHE             VARCHAR2(30)    NOT NULL,
    FORNECEDOR            VARCHAR2(25)    NULL,
    MODULO                VARCHAR2(50)    NULL,
    FIGURA                VARCHAR2(99)    NULL,
    STATUS                NUMBER          NULL,
    PRECO                 BINARY_DOUBLE   NULL,
    IDCLIENTE             NUMBER          NULL,
    DESATIVADOSN          CHAR(1)         NOT NULL, -- bit
    DATACRIACAOREGISTRO   DATE            NULL,
    CONSTRAINT PK_CLICHES PRIMARY KEY (CODCLICHE)
)
