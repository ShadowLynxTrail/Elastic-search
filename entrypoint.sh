#!/bin/sh
set -e

echo "Ждём PostgreSQL..."
until python -c "import psycopg2; psycopg2.connect(host='db', user='postgres', password='postgres', dbname='test_search_db')" 2>/dev/null; do
  sleep 1
done

echo "Ждём Elasticsearch..."
until curl -s http://elasticsearch:9200 >/dev/null; do
  sleep 1
done

echo "Индексируем документы..."
python index_documents.py

echo "Запускаем API..."
echo ""
echo "======================================================"
echo "  ✅ API готово!"
echo "  📖 Swagger: http://localhost:8000/docs"
echo "======================================================"
echo ""
exec uvicorn main:app --host 0.0.0.0 --port 8000