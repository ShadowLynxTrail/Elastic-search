import os
os.environ["PGCLIENTENCODING"] = "UTF8"

from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from elasticsearch import Elasticsearch

app = FastAPI(title="Simple Document Search")

# Читаем из переменных окружения (с дефолтами для локального запуска)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "test_search_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")

es = Elasticsearch(ES_HOST)
INDEX_NAME = "documents"

def get_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, client_encoding="utf8",
        cursor_factory=RealDictCursor,
    )

class Document(BaseModel):
    id: int
    rubrics: list[str] | None = None
    text: str
    created_date: datetime

@app.get("/search", response_model=list[Document])
def search(q: str):
    response = es.search(index=INDEX_NAME, query={"match": {"text": q}}, size=20)
    ids = [int(hit["_id"]) for hit in response["hits"]["hits"]]
    if not ids:
        return []
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, rubrics, text, created_date FROM documents
        WHERE id = ANY(%s) ORDER BY created_date DESC LIMIT 20;
    """, (ids,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM documents WHERE id = %s;", (doc_id,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if es.exists(index=INDEX_NAME, id=str(doc_id)):
        es.delete(index=INDEX_NAME, id=str(doc_id))
        es.indices.refresh(index=INDEX_NAME)
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    return {"status": "deleted", "id": doc_id}