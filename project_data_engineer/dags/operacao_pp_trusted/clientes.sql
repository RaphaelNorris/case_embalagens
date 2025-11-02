CREATE TABLE CLIENTES (
    IDCLIENTE                      NUMBER           NOT NULL,
    CLIENTE                        VARCHAR2(50)     NOT NULL,
    CODCLIENTE                     VARCHAR2(30)     NOT NULL,
    CODREPRESENTANTE               NUMBER           NULL,
    TOLMAIS                        NUMBER(3)        NOT NULL, -- tinyint
    TOLMENOS                       NUMBER(3)        NOT NULL, -- tinyint
    RAZAOSOCIAL                    VARCHAR2(99)     NOT NULL,
    EXIGELAUDO                     CHAR(1)          NOT NULL, -- bit
    IDUNICOREGISTRO                RAW(16)          NOT NULL, -- uniqueidentifier
    ACEITAPALETEINCOMPLETO         NUMBER(3)        NOT NULL, -- tinyint
    DESCACEITAPALETEINCOMPLETO     VARCHAR2(100)    NULL,
    DATACRIACAO                    DATE             NOT NULL,
    DATAULTMODIF                   DATE             NOT NULL,
    CONSTRAINT PK_CLIENTES PRIMARY KEY (IDCLIENTE)
)
