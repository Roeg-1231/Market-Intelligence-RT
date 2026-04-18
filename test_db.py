import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mercador_rt")

print(f"Connecting to: user={DB_USER} pass={DB_PASSWORD} host={DB_HOST} port={DB_PORT} db={DB_NAME}")

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    print("Conexión exitosa a psycopg2!!")
    conn.close()
except Exception as e:
    print("Raw exception repr:")
    print(repr(e))
    # intentar obtener bytes si es un OperationalError string decode issue
    try:
        import traceback
        traceback.print_exc()
    except:
        pass
