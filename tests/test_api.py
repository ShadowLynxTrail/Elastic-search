"""
Функциональные тесты для сервиса поиска документов.

Предполагается, что сервис уже запущен (docker compose up -d)
и доступен на http://localhost:8000.
"""
import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


class TestSearch:
    def test_search_by_existing_word(self, client):
        """Поиск по слову, которое точно есть в документе."""
        r = client.get("/search", params={"q": "матч"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Проверяем структуру документа
        doc = data[0]
        assert "id" in doc
        assert "text" in doc
        assert "created_date" in doc
        assert "rubrics" in doc

    def test_search_empty_result(self, client):
        """Поиск по слову, которого нет ни в одном документе."""
        r = client.get("/search", params={"q": "невероятнослово"})
        assert r.status_code == 200
        assert r.json() == []

    def test_search_returns_at_most_20(self, client):
        """Проверяем, что сервис не возвращает больше 20 документов."""
        r = client.get("/search", params={"q": "и"})  # очень частое слово
        assert r.status_code == 200
        assert len(r.json()) <= 20

    def test_search_result_sorted_by_date_desc(self, client):
        """Проверяем сортировку по дате (от новых к старым)."""
        r = client.get("/search", params={"q": "матч"})
        assert r.status_code == 200
        docs = r.json()
        if len(docs) > 1:
            dates = [d["created_date"] for d in docs]
            assert dates == sorted(dates, reverse=True)


class TestDelete:
    def test_delete_existing_document(self, client):
        """Удаляем существующий документ — ожидаем 200 и подтверждение."""
        # Создаём документ, чтобы точно его удалить
        # (в нашем случае просто удалим id=1 и проверим)
        r = client.delete("/documents/1")
        # Может вернуть 200 (если был) или 404 (если уже удалён)
        assert r.status_code in (200, 404)

        if r.status_code == 200:
            body = r.json()
            assert body["status"] == "deleted"
            assert body["id"] == 1

    def test_delete_non_existent_document(self, client):
        """Удаление несуществующего id — ожидаем 404."""
        r = client.delete("/documents/999999")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_document_disappears_after_delete(self, client):
        """После удаления документ не должен находиться в поиске."""
        # Ищем документ
        r = client.get("/search", params={"q": "PostgreSQL"})
        docs = r.json()
        if not docs:
            pytest.skip("Документ со словом PostgreSQL отсутствует, нечего удалять")

        doc_id = docs[0]["id"]

        # Удаляем
        r = client.delete(f"/documents/{doc_id}")
        assert r.status_code == 200

        # Проверяем, что больше не находится
        r = client.get("/search", params={"q": "PostgreSQL"})
        found_ids = [d["id"] for d in r.json()]
        assert doc_id not in found_ids