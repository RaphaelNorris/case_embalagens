CREATE TABLE CLIENTES (
    IDCLIENTE                      NUMBER           NOT NULL,
    CLIENTE                        VARCHAR2(50)     NOT NULL,
    CODCLIENTE                     VARCHAR2(30)     NOT NULL,
    CODREPRESENTANTE               NUMBER           NULL,
    TOLMAIS                        NUMBER(3)        NOT NULL, -- tinyint
    TOLMENOS                       NUMBER(3)        NOT NULL, -- tinyint
    TIPOOBS1                       VARCHAR2(15)     NULL,
    OBS1                           VARCHAR2(255)    NULL,
    TIPOOBS2                       VARCHAR2(15)     NULL,
    OBS2                           VARCHAR2(255)    NULL,
    TIPOOBS3                       VARCHAR2(15)     NULL,
    OBS3                           VARCHAR2(255)    NULL,
    TIPOOBS4                       VARCHAR2(15)     NULL,
    OBS4                           VARCHAR2(255)    NULL,
    TIPOABC                        VARCHAR2(5)      NULL,
    CODSEGMENTO                    VARCHAR2(20)     NULL,
    PREFERENCIALSN                 CHAR(1)          NOT NULL, -- bit
    CLIENTELISTASN                 CHAR(1)          NOT NULL, -- bit
    AGRUPAMENTO                    VARCHAR2(20)     NULL,
    CLIENTE_FORNECEDOR             NUMBER(3)        NULL,    -- tinyint
    DESCRCLIENTE_FORNECEDOR        VARCHAR2(30)     NULL,
    RAZAOSOCIAL                    VARCHAR2(99)     NOT NULL,
    CODIGOERP                      VARCHAR2(60)     NULL,
    ETIQUETA                       VARCHAR2(50)     NULL,
    EXIGELAUDO                     CHAR(1)          NOT NULL, -- bit
    LAUDO                          VARCHAR2(50)     NULL,
    EMAILLAUDO                     VARCHAR2(1000)   NULL,
    CARTAORCAMENTO                 VARCHAR2(50)     NULL,
    NRETIQUETAS                    NUMBER(3)        NULL,    -- tinyint
    IDUNICOREGISTRO                RAW(16)          NOT NULL, -- uniqueidentifier
    ACEITAPALETEINCOMPLETO         NUMBER(3)        NOT NULL, -- tinyint
    DESCACEITAPALETEINCOMPLETO     VARCHAR2(100)    NULL,
    IDATENDENTEVENDA               NUMBER           NULL,
    CONTATOFATURAMENTO             VARCHAR2(100)    NULL,
    IDCLASSFISCAL                  NUMBER           NULL,
    DATACRIACAO                    DATE             NOT NULL,
    USUARIOCRIACAO                 VARCHAR2(102)    NULL,
    DATAULTMODIF                   DATE             NOT NULL,
    USUARIOULTMODIF                VARCHAR2(102)    NULL,
    RAZAOTRAVACOMPOSICAO           VARCHAR2(50)     NULL,
    CUSTOFINANCEIROADICIONAL       BINARY_DOUBLE    NOT NULL,
    CUSTOADICTRANSPORTEPORPALETE   BINARY_DOUBLE    NOT NULL,
    CUSTOADICTRANSPPORKG_PALETIZ   BINARY_DOUBLE    NOT NULL,
    CUSTOADICTRANSPPORKG_NPALETIZ  BINARY_DOUBLE    NOT NULL,
    CUSTOADICTRANSPPORM2_PALETIZ   BINARY_DOUBLE    NOT NULL,
    CUSTOADICTRANSPPORM2_NPALETIZ  BINARY_DOUBLE    NOT NULL,
    CUSTOADICTRANSPPORPECA_PALETIZ BINARY_DOUBLE    NOT NULL,
    CUSTOADICTRANSPPORPECANPALETIZ BINARY_DOUBLE   NOT NULL,
    USOGERALSTR1                   VARCHAR2(255)    NULL,
    USOGERALSTR2                   VARCHAR2(255)    NULL,
    USOGERALNUM1                   BINARY_DOUBLE    NULL,
    USOGERALNUM2                   BINARY_DOUBLE    NULL,
    EXIGECHAPAUNITIZADA            CHAR(1)          NOT NULL, -- bit
    EXIGEAGENDAMENTOENTREGAS       CHAR(1)          NOT NULL, -- bit
    CLIENTEPROSPECTO               CHAR(1)          NULL,    -- bit
    IMPRIMELOGOTIPO                CHAR(1)          NOT NULL, -- bit
    PALETIZADO                     NUMBER(5)        NOT NULL, -- smallint
    FACESOPPOSTAS                  NUMBER(5)        NOT NULL, -- smallint
    ESPELHO                        NUMBER(5)        NOT NULL, -- smallint
    CANTONEIRAS                    NUMBER(5)        NOT NULL, -- smallint
    FILME                          NUMBER(5)        NOT NULL, -- smallint
    ORELHASINVERTIDAS              NUMBER(5)        NOT NULL, -- smallint
    PACOTESLARGURA                 NUMBER           NULL,
    PACOTOSCOMPRIMENTO             NUMBER           NULL,
    PACOTESALTURA                  NUMBER           NULL,
    IDPALETE                       NUMBER           NULL,
    EMPILHAMENTOMAXIMO             NUMBER           NULL,
    PRESSAODEARQUEAMENTO           NUMBER           NULL,
    FITASLARGPALETE                NUMBER           NULL,
    FITASCOMMPALETE                NUMBER           NULL,
    CONSTRAINT PK_CLIENTES PRIMARY KEY (IDCLIENTE)
)
