import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

def load_env_oracle()->str:
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    port = os.getenv("PORT", "1521") 
    service_name = os.getenv("SERVICE_NAME")


    conn = oracledb.connect(
        user=user,
        password=password,
        host =host,
        port = port,
        service_name = service_name
    )
    return conn
  
