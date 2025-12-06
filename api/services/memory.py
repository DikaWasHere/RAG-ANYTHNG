import os
import json
import redis
from datetime import datetime
from api.services.db import get_postgres_conn


# === Redis ===
redis_client = redis.Redis(
    host="localhost",    # ganti sesuai env
    port=6379,
    decode_responses=True
)


# ============ Redis Chat Memory =============

def get_chat_history(chat_id: str):
    key = f"chat:{chat_id}"
    history_json = redis_client.get(key)
    return json.loads(history_json) if history_json else []

def save_message_redis(chat_id: str, role: str, content: str):
    key = f"chat:{chat_id}"
    history = get_chat_history(chat_id)
    history.append({"role": role, "content": content})
    redis_client.set(key, json.dumps(history))

# ============ Postgres Persistent Chat =============

def save_message_postgres(chat_id, doc_id, user_id, role, content):
    conn = get_postgres_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO chat_messages (chat_id, doc_id, user_id, role, content, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (chat_id, doc_id, user_id, role, content, datetime.now()))
        conn.commit()
    conn.close()

def get_chat_history_postgres(chat_id):
    conn = get_postgres_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT role, content FROM chat_messages
            WHERE chat_id = %s ORDER BY timestamp ASC
        """, (chat_id,))
        rows = cur.fetchall()
    conn.close()
    return rows
