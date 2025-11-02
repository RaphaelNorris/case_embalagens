CREATE TABLE FI (
    CODFI            VARCHAR2(30)    NOT NULL,
    FIGURA           VARCHAR2(99)    NULL,
    DESATIVADOSN     CHAR(1)         NOT NULL, -- bit
    COR1             VARCHAR2(15)    NULL,
    COR2             VARCHAR2(15)    NULL,
    CONSUMOCOR2      NUMBER          NULL,
    VISCOSIDADECOR2  NUMBER          NULL,
    COR3             VARCHAR2(15)    NULL,
    CONSUMOCOR3      NUMBER          NULL,
    COR4             VARCHAR2(15)    NULL,
    CONSUMOCOR4      NUMBER          NULL,
    CONSTRAINT PK_FI PRIMARY KEY (CODFI)
)
