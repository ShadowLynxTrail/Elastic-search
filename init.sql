CREATE TABLE IF NOT EXISTS documents (
id SERIAL PRIMARY KEY,
rubrics TEXT[],
text TEXT NOT NULL,
created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO documents (rubrics, text, created_date) VALUES
(ARRAY['спорт'], 'Сборная России выиграла товарищеский матч.', NOW() - INTERVAL '2 days'),
(ARRAY['технологии'], 'PostgreSQL 17 показывает отличную производительность.', NOW()),
(ARRAY['новости'], 'Центральный банк снизил ключевую ставку.', NOW() + INTERVAL '1 hour');