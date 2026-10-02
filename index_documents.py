import os
os.environ["PGCLIENTENCODING"] = "UTF8"

import psycopg2
from psycopg2.extras import RealDictCursor
from elasticsearch import Elasticsearch

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_NAME", "test_search_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
    client_encoding="utf8",
    cursor_factory=RealDictCursor,
)
es = Elasticsearch(os.getenv("ES_HOST", "http://localhost:9200"))

INDEX_NAME = "documents"

# --- 1. Удаляем старый индекс (если был), чтобы начать с чистого листа ---
if es.indices.exists(index=INDEX_NAME):
    es.indices.delete(index=INDEX_NAME)
    print(f"Старый индекс '{INDEX_NAME}' удалён.")

# --- 2. Создаём новый индекс ---
es.indices.create(index=INDEX_NAME)
print(f"Индекс '{INDEX_NAME}' создан.")

# --- 3. Читаем документы из БД ---
cur = conn.cursor()
cur.execute("SELECT id, text FROM documents;")
rows = cur.fetchall()

# --- 4. Индексируем каждый документ в ЭС ---
for row in rows:
    es.index(
        index=INDEX_NAME,
        id=row["id"],
        document={"text": row["text"]},
    )
    print(f"  → Проиндексирован документ id={row['id']}")

# --- 5. Refresh, чтобы изменения сразу стали видны поиску ---
es.indices.refresh(index=INDEX_NAME)
print(f"\n✅ Всего проиндексировано: {len(rows)} документов.")

cur.close()
conn.close()