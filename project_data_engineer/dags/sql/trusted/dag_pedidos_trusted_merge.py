from __future__ import annotations
from datetime import datetime, date
from typing import Any, Dict, List, Iterable

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
import oracledb

ORACLE_CONN_ID_RAW = "oracle_raw"
ORACLE_CONN_ID_TRUSTED = "oracle_trusted"

TARGET_TABLE = "PEDIDOS"

# COLUNAS QUE EXISTEM NA TRUSTED - baseado na tabela destino que você enviou
TRUSTED_COLS = [
    "IDPEDIDOS", "PEDIDO", "ITEM", "ITEMPEDIDO", "STATUSPEDIDO", "DESCRSTATUSPEDIDO",
    "SUSPENSO", "SUSPOUCANCEL", "VERSAO", "IDCLIENTE", "REFERENCIA", "CODIGOREFERENCIA",
    "TIPOABNT", "PECASPORUNIDADE", "IDTIPOFT2", "UNIDADESPORCONJUNTO", "PECASPORCONJUNTO",
    "EXIGELAUDO", "GRAMATURA", "MULLENMINIMO", "CRUSHMINIMO", "COLUNAMINIMO",
    "COBBINTMAXIMO", "COBBEXTMAXIMO", "ESPESSURA", "COMPRESSAO", "CHAPA", "COMPOSICAO",
    "LARGURA", "REFILOLARGURA", "COMPRIMENTO", "REFILOCOMPRIMENTO", "MULTLARG", "MULTCOMP",
    "ARRANJO", "REFUGOCLIENTE", "PESOPECA", "VINCOLARG1", "VINCOLARG2", "VINCOLARG3",
    "VINCOCOMP1", "VINCOCOMP2", "VINCOCOMP3", "VINCOCOMP4", "VINCOCOMP5",
    "LAP", "PROLONGLAP", "LAPNOCOMP", "LAPINTERNO", "LAPPRIMVINCO", "REFILADO",
    "RESINAINTERNA", "RESINAINTERNASN", "FECHAMENTO", "AMARRADO", "FITILHOSLARGPACOTE",
    "PALETIZADO", "DESCRPALETIZADO", "PACOTESLARGURA", "PACOTESCOMPRIMENTO", "PACOTESALTURA",
    "PECASPORPACOTE", "PECASPORPALETE", "UNIDADESPORPALETE", "PACOTESPORPALETE",
    "FITASLARGPALETE", "FITASCOMPPALETE", "ESPELHO", "FILME", "FACA", "CODFI", "COR1",
    "CONSUMOCOR1", "COR2", "CONSUMOCOR2", "COR3", "CONSUMOCOR3", "COR4", "CONSUMOCOR4",
    "NRCORES", "TOLMAIS", "TOLMENOS", "TIPOOBS1", "OBS1", "TIPOOBS2", "OBS2", "TIPOOBS3",
    "OBS3", "TIPOOBS4", "OBS4", "TIPOOBS5", "OBS5", "TIPOOBS6", "OBS6", "TIPOOBS9", "OBS9",
    "DATAENTREGA1", "DATAENTREGA2", "QUANTIDADEPEDIDA", "QUANTIDADEPEDIDAMIN",
    "QUANTIDADEPEDIDAMAX", "TIPOENTREGA", "DESCTIPOENTREGA", "LARGURAINTERNA",
    "COMPRIMENTOINTERNO", "ALTURAINTERNA", "LARGPECA", "COMPPECA", "DISTANCIA",
    "CONDICAODEPAGAMENTO", "DATACRIACAO", "DATAENTREGAORIGINAL", "DATAULTIMAALTERACAOFT",
    "DESCFLAGESTOQUEOUTERCEIROS", "DESCRTIPODOPEDIDO", "IMPRIMELOGOTIPO",
    "COMPPACOTE", "LARGPACOTE", "ALTURAPACOTE", "COMPPALETEFECHADO", "LARGPALETEFECHADO",
    "ALTURAPALETEFECHADO", "PESOCAIXA", "PEDCLIENTE", "DESCRTRAVACOMPOSICAO",
    "PATHFIGURADOLASTRO", "EMPILHAMENTOMAXIMO", "IDPALETE", "PEDIDO_ERP", "ITEM_ERP",
    "PRODUTO_ERP", "DATACRIACAOREGISTRO", "IDUNICOREGISTRO", "IDUSUARIOULTMODIF",
    "ULTMODIFICACAO", "CODREPRESENTANTE", "CODSEGMENTO", "AREABRUTAPECACOMREFILOS",
    "AREABRUTAPECA", "AREALIQUIDAPECA", "AREABRUTACHAPA", "AREALIQUIDACHAPA",
    "VOLUMEPALETEFECHADOM3", "VOLUMEPACOTEFECHADOM3", "VOLUMEFECHADOPEDIDO",
    "ORIGEMPEDIDO", "DESCORIGEMPEDIDO", "TIPOGERACAOPED", "DESCTIPOGERACAOPED", "CHAVE_CHAPA"
]

def _make_oracle_conn(conn_id: str):
    """Cria conexão Oracle - igual à DAG funcional"""
    try:
        c = BaseHook.get_connection(conn_id)
        extra = c.extra_dejson or {}
        service_name = extra.get("service_name")
        sid = extra.get("sid")
        port = c.port or 1521

        if service_name:
            dsn = oracledb.makedsn(c.host, port, service_name=service_name)
        elif sid:
            dsn = oracledb.makedsn(c.host, port, sid=sid)
        else:
            dsn = oracledb.makedsn(c.host, port, service_name=c.schema)

        return oracledb.connect(user=c.login, password=c.password, dsn=dsn)
        
    except Exception as e:
        print(f"[CONN] ERRO na conexão {conn_id}: {str(e)}")
        raise

def _chunk(it: Iterable[Dict[str, Any]], size: int) -> Iterable[List[Dict[str, Any]]]:
    """Divide em lotes menores - igual à DAG funcional"""
    buf: List[Dict[str, Any]] = []
    for x in it:
        buf.append(x)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf

def _to_date_like(v: Any) -> Any:
    """Converte para datetime - similar à DAG funcional"""
    if v is None or isinstance(v, (datetime, date)):
        return v
    try:
        return datetime.fromisoformat(str(v))
    except Exception:
        return v

def _convert_value(col_name: str, value: Any) -> Any:
    """Converte TODOS os valores para string - exceto datas e RAW"""
    if value is None:
        return None
    
    # Apenas TIMESTAMP e RAW mantêm tipos específicos
    if col_name in ["DATAENTREGA1", "DATAENTREGA2", "DATACRIACAO", "DATAENTREGAORIGINAL",
                   "DATAULTIMAALTERACAOFT", "DATACRIACAOREGISTRO", "ULTMODIFICACAO"]:
        dt_val = _to_date_like(value)
        if dt_val is not None and isinstance(dt_val, datetime):
            return dt_val.strftime('%Y/%m/%d %H:%M:%S.000')
        return dt_val
        
    elif col_name == "IDUNICOREGISTRO":
        return value  # Mantém como está para RAW16
        
    else:
        # TODAS AS OUTRAS COLUNAS - CONVERTE PARA STRING
        return str(value) if value is not None else None

def etl_pedidos_raw_to_trusted(**context):
    # CONFIGURAÇÃO DE PAGINAÇÃO - EXATAMENTE IGUAL À DAG FUNCIONAL
    page_size = 20000
    offset = 0
    total_processed = 0
    batch_count = 0
    
    print(f"[PEDIDOS] Iniciando ETL para tabela {TARGET_TABLE} - SEM LIMPEZA DA TABELA DESTINO")

    # **ALTERAÇÃO: REMOVIDA a limpeza da tabela destino**
    # A tabela TRUSTED.PEDIDOS manterá seus dados existentes
    # Novos registros serão inseridos/atualizados via MERGE

    while True:  # EXATAMENTE IGUAL À DAG FUNCIONAL

        # Query com paginação - usando APENAS colunas da TRUSTED
        sql = f"""
            SELECT {', '.join(TRUSTED_COLS)} FROM PEDIDOS 
            ORDER BY IDPEDIDOS
            OFFSET {offset} ROWS 
            FETCH NEXT {page_size} ROWS ONLY
        """
        
        # Conecta na RAW para cada página - IGUAL À DAG FUNCIONAL
        src_conn = _make_oracle_conn(ORACLE_CONN_ID_RAW)
        try:
            with src_conn.cursor() as cur:
                cur.execute(sql)
                columns = [column[0] for column in cur.description]
                rows = []
                for row in cur.fetchall():
                    rows.append(dict(zip(columns, row)))
            
            print(f"RAW -> Página {batch_count + 1}: {len(rows)} registros extraídos da tabela PEDIDOS.")

            if not rows:
                print(f"Todas as páginas processadas. Total: {total_processed} registros.")
                break

            # 2) Processa os dados da página atual com conversão de tipos
            payload: List[Dict[str, Any]] = []
            for r in rows:
                try:
                    processed_rec = {}
                    
                    for c in columns:
                        value = r.get(c)
                        processed_rec[c] = _convert_value(c, value)

                    payload.append(processed_rec)
                except Exception as e:
                    print(f"Erro ao processar linha: {str(e)}. Linha ignorada.")
                    continue

            if payload:
                # 3) Processa o lote atual (MERGE no Oracle) - IGUAL À DAG FUNCIONAL
                _process_batch_pedidos(payload, batch_count + 1, columns)
                total_processed += len(payload)
                print(f"Página {batch_count + 1} processada: {len(payload)} registros válidos (total acumulado: {total_processed})")
            else:
                print(f"Página {batch_count + 1} sem registros válidos, pulando.")

            # Prepara próxima página - IGUAL À DAG FUNCIONAL
            batch_count += 1
            offset += page_size
            
            # Limpa memória - IGUAL À DAG FUNCIONAL
            del rows
            del payload

        except Exception as e:
            print(f"Erro ao extrair dados da RAW (página {batch_count + 1}): {str(e)}")
            raise
        finally:
            src_conn.close()

    if total_processed == 0:
        print("Nenhum dado válido para processar.")
        return

    print(f"ETL concluída: {total_processed} registros processados com sucesso.")


def _process_batch_pedidos(payload, batch_number, columns):
    """Processa um lote de registros no Oracle com MERGE - com DEBUG detalhado"""
    
    # Prepara o MERGE dinâmico com as colunas que existem na TRUSTED
    pk = "IDPEDIDOS"
    non_pk_cols = [c for c in columns if c != pk]

    select_dual = ", ".join([
        f"TO_TIMESTAMP(:{c}, 'YYYY/MM/DD HH24:MI:SS.FF3') AS {c}" if c in [
            "DATAENTREGA1", "DATAENTREGA2", "DATACRIACAO", "DATAENTREGAORIGINAL",
            "DATAULTIMAALTERACAOFT", "DATACRIACAOREGISTRO", "ULTMODIFICACAO"
        ] else f":{c} {c}" 
        for c in columns
    ])
    update_set = ", ".join([f"t.{c} = s.{c}" for c in non_pk_cols])
    insert_cols = ", ".join(columns)
    insert_vals = ", ".join([f"s.{c}" for c in columns])

    merge_sql = f"MERGE INTO PEDIDOS t USING (SELECT {select_dual} FROM dual) s ON (t.{pk} = s.{pk}) WHEN MATCHED THEN UPDATE SET {update_set} WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})"

    dst = _make_oracle_conn(ORACLE_CONN_ID_TRUSTED)
    try:
        cur = dst.cursor()
        
        # Executa em sub-lotes para melhor performance - IGUAL À DAG FUNCIONAL
        for sub_batch_num, sub_batch in enumerate(_chunk(payload, size=1000)):
            print(f"Processando sub-lote {sub_batch_num + 1} com {len(sub_batch)} registros")
            
            try:
                cur.executemany(merge_sql, sub_batch)
            except Exception as e:
                print(f"ERRO DETALHADO no sub-lote {sub_batch_num + 1}:")
                print(f"Erro completo: {str(e)}")
                
                # Verifica o primeiro registro do sub-lote que falhou
                if sub_batch:
                    first_record = sub_batch[0]
                    print("Primeiro registro do sub-lote que falhou:")
                    for col, val in first_record.items():
                        print(f"  {col}: {val} (tipo: {type(val).__name__})")
                
                # Tenta executar um por um para identificar o registro exato que causa o erro
                print("Tentando identificar registro específico que causa erro...")
                for i, record in enumerate(sub_batch):
                    try:
                        cur.execute(merge_sql, record)
                        dst.commit()
                    except Exception as single_error:
                        print(f"ERRO no registro {i}:")
                        print(f"  Erro: {str(single_error)}")
                        print(f"  Registro problemático:")
                        for col, val in record.items():
                            print(f"    {col}: {val} (tipo: {type(val).__name__})")
                        # Para após encontrar o primeiro erro
                        raise single_error
                
                raise e
        
        dst.commit()
        print(f"TRUSTED <- Lote {batch_number}: {len(payload)} registros processados com sucesso.")
            
    except Exception as e:
        print(f"Erro ao fazer MERGE no Oracle (lote {batch_number}): {str(e)}")
        dst.rollback()
        raise
    finally:
        dst.close()

# -----------------
# DAG para PEDIDOS - IGUAL À DAG FUNCIONAL
# -----------------
with DAG(
    dag_id="etl_pedidos_raw_to_trusted_otimizadao",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["etl", "oracle", "pedidos", "trusted"],
):
    PythonOperator(
        task_id="merge_upsert_pedidos",
        python_callable=etl_pedidos_raw_to_trusted,
    )