import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def create_chat_messages_table():
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS chat_messages (
        id SERIAL PRIMARY KEY,
        chat_id VARCHAR NOT NULL,
        doc_id VARCHAR NOT NULL,
        user_id VARCHAR NOT NULL,
        role VARCHAR NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    with conn:
        with conn.cursor() as cur:
            cur.execute(create_table_sql)
            print("✅ Tabel chat_messages berhasil dibuat atau sudah ada.")
    conn.close()

if __name__ == "__main__":
    create_chat_messages_table()
