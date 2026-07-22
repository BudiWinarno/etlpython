import urllib.parse
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

SERVER = os.getenv("SQLSERVER_HOST")
PORT = os.getenv("SQLSERVER_PORT", "1433")
DATABASE = os.getenv("SQLSERVER_DATABASE")
USERNAME = os.getenv("SQLSERVER_USERNAME")
PASSWORD = os.getenv("SQLSERVER_PASSWORD")

# Encode password kalau ada karakter khusus
PASSWORD = urllib.parse.quote_plus(PASSWORD)

connection_string = (
    f"mssql+pyodbc://{USERNAME}:{PASSWORD}"
    f"@{SERVER}:{PORT}/{DATABASE}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

engine_sqlserver = create_engine(connection_string)

# ==========================
# Test Koneksi Database
# ==========================
if __name__ == "__main__":
    print("HOST :", SERVER)
    print("DB   :", DATABASE)

    with engine_sqlserver.connect() as conn:
        print("Koneksi SQL Server Berhasil!")