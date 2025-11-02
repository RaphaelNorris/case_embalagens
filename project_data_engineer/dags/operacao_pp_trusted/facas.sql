CREATE TABLE FACAS (
    CODFACA               VARCHAR2(30)    NOT NULL,
    TIPO                  NUMBER          NULL,
    DESCRTIPOFACA         VARCHAR2(30)    NULL,
    FORNECEDOR            VARCHAR2(25)    NULL,
    MODULO                VARCHAR2(50)    NULL,
    ARQUIVO               VARCHAR2(50)    NULL,
    PECASPORFACA          NUMBER          NOT NULL,
    FIGURA                VARCHAR2(99)    NULL,
    STATUS                NUMBER          NULL,
    PRECO                 BINARY_DOUBLE   NULL,
    COMPLAMINA            NUMBER          NULL,
    IDCLIENTE             NUMBER          NULL,
    OBS                   VARCHAR2(1000)  NULL,
    DESATIVADOSN          CHAR(1)         NOT NULL, -- bit
    DATACRIACAOREGISTRO   DATE            NULL,
    CONSTRAINT PK_FACAS PRIMARY KEY (CODFACA)
)
