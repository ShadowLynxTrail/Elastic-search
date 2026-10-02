# Simple Document Search

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791)](https://www.postgresql.org/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.15-005571)](https://www.elastic.co/)
[![Docker](https://img.shields.io/badge/Docker-compose-2496ED)](https://www.docker.com/)

Поисковик по текстам документов: PostgreSQL как хранилище, Elasticsearch как поисковый индекс, FastAPI как API.

## Стек
- Python 3.12, FastAPI, Uvicorn
- PostgreSQL 17
- Elasticsearch 8.15
- Docker / Docker Compose

## Запуск
```bash
docker compose up --build 
```
# API
```
- GET /search?q=<запрос>
```
— поиск до 20 документов, отсортированных по дате.
```
- DELETE /documents/{id}
 ```
— удаление документа из БД и индекса.

### После старта

Swagger: 
```
http://localhost:8000/docs
```
Elasticsearch:
```
http://localhost:9200
```
# Архитектура
1. **_init.sql_** создаёт таблицу documents и наполняет её при первом старте PostgreSQL.

2. **_entrypoint.sh_** дожидается готовности БД и ЭС, затем запускает index_documents.py, который переносит id и text документов в Elasticsearch.

3. FastAPI-сервис:

_**GET /search**_ сначала ищет релевантные id в Elasticsearch, затем достаёт полные данные из PostgreSQL по этим id.

**_DELETE /documents/{id}_** удаляет документ из обеих систем.

# Примеры
bash
curl "http://localhost:8000/search?q=матч"

curl -X DELETE "http://localhost:8000/documents/1"

## Тесты

Требуется запущенный сервис:

```bash
docker compose up -d
pip install -r requirements.txt
pytest tests/ -v
```
# Cтруктура проекта

```
SQL_testing/
├── main.py
├── index_documents.py
├── entrypoint.sh
├── init.sql
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── docs.json
├── README.md
├── pytest.ini 
└── tests/
  └── test_api.py
```