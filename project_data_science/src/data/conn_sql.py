import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os

# Carregar .env
load_dotenv()

def query_sqlserver(query):
    """Conexão SQL Server usando pyodbc (mais estável que pymssql)"""
    try:
        server = os.getenv('SQLSERVER_HOST', '172.16.16.40')
        database = os.getenv('SQLSERVER_DATABASE', 'TRIMBOX')
        username = os.getenv('SQLSERVER_USER', 'amcom')
        password = os.getenv('SQLSERVER_PASSWORD', 'YK9ZGrzjlxo2')
        
        # Tentar diferentes drivers ODBC
        drivers = [
            'ODBC Driver 17 for SQL Server',
            'ODBC Driver 13 for SQL Server', 
            'SQL Server Native Client 11.0',
            'SQL Server'
        ]
        
        for driver in drivers:
            try:
                conn_string = (
                    f'DRIVER={{{driver}}};'
                    f'SERVER={server};'
                    f'DATABASE={database};'
                    f'UID={username};'
                    f'PWD={password};'
                    f'TrustServerCertificate=yes;'
                )
                
                conn = pyodbc.connect(conn_string, timeout=10)
                df = pd.read_sql(query, conn)
                conn.close()
                
                print(f"✅ Conectado usando: {driver}")
                return df
                
            except Exception as e:
                continue
        
        raise Exception("Nenhum driver ODBC funcionou")
        
    except Exception as e:
        print(f"Erro: {e}")
        return pd.DataFrame()

# Testar
if __name__ == "__main__":
    print("Testando conexão SQL Server via pyodbc...")
    df = query_sqlserver("SELECT COUNT(*) as total FROM dbo.Clientes")
    
    if not df.empty:
        print(f"Total de clientes: {df.iloc[0]['total']}")
    else:
        print("Falha na conexão")