CREATE TABLE FACAS (
    CODFACA               VARCHAR2(30)    NOT NULL,
    TIPO                  NUMBER          NULL,
    DESCRTIPOFACA         VARCHAR2(30)    NULL,
    FORNECEDOR            VARCHAR2(25)    NULL,
    MODULO                VARCHAR2(50)    NULL,
    ARQUIVO               VARCHAR2(50)    NULL,
    LARGURA               NUMBER          NULL,
    COMPRIMENTO           NUMBER          NULL,
    PECASPORFACA          NUMBER          NOT NULL,
    LOCALIZACAO           VARCHAR2(50)    NULL,
    FIGURA                VARCHAR2(99)    NULL,
    STATUS                NUMBER          NULL,
    PRECO                 BINARY_DOUBLE   NULL,
    COMPLAMINA            NUMBER          NULL,
    IDCLIENTE             NUMBER          NULL,
    OBS                   VARCHAR2(1000)  NULL,
    CODIGOERP             VARCHAR2(30)    NULL,
    CHAVEESTADOFERRAMENTA NUMBER          NOT NULL,
    DESATIVADOSN          CHAR(1)         NOT NULL, -- bit
    REFUGOCLIENTE         BINARY_DOUBLE   NULL,
    DATACRIACAOREGISTRO   DATE            NULL,
    CONSTRAINT PK_FACAS PRIMARY KEY (CODFACA)
)
