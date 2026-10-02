import os
os.environ["PGCLIENTENCODING"] = "UTF8"

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="test_search_db",
    user="postgres",
    password="postgres",
    client_encoding="utf8"
)
cur = conn.cursor()

# --- ПОИСК ---
search_query = "Python"
cur.execute("""
    SELECT * FROM documents 
    WHERE text ILIKE %s 
    ORDER BY created_date DESC 
    LIMIT 20;
""", (f'%{search_query}%',))
rows = cur.fetchall()
print(f"🔍 Найдено по запросу '{search_query}': {len(rows)} шт.")
for row in rows:
    print(f"   ID: {row[0]} | Текст: {row[2]}")

# --- УДАЛЕНИЕ С ПРОВЕРКОЙ ---
doc_id_to_delete = 5
cur.execute("DELETE FROM documents WHERE id = %s;", (doc_id_to_delete,))
conn.commit()

# ✅ Проверяем, сколько строк РЕАЛЬНО удалено
if cur.rowcount == 0:
    print(f"\n⚠️ Документ с ID {doc_id_to_delete} не найден. Ничего не удалено.")
else:
    print(f"\n🗑️ Удалено строк: {cur.rowcount} (ID {doc_id_to_delete}).")

# ✅ Повторный SELECT — убеждаемся, что его больше нет
cur.execute("SELECT COUNT(*) FROM documents WHERE id = %s;", (doc_id_to_delete,))
count = cur.fetchone()[0]
if count == 0:
    print(f"✅ Проверка: документ с ID {doc_id_to_delete} действительно удалён из БД.")
else:
    print(f"❌ Проверка: документ всё ещё в базе! Что-то не так.")

cur.close()
conn.close()