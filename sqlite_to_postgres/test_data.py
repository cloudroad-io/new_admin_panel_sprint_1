import sqlite3
import psycopg
from psycopg.rows import dict_row
import pytest
import uuid

POSTGRES_DSL = {
    'dbname': 'movies_database',
    'user': 'app',
    'password': '123qwe',
    'host': '127.0.0.1',
    'port': 5432
}

TABLES = [
    'genre',
    'film_work',
    'person',
    'genre_film_work',
    'person_film_work'
]

# Поля, которые не сравниваем
FIELDS_TO_IGNORE = ['created_at', 'updated_at']

@pytest.fixture(scope='module')
def sqlite_connection():
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

@pytest.fixture(scope='module')
def postgres_connection():
    with psycopg.connect(**POSTGRES_DSL, row_factory=dict_row) as conn:
        yield conn

def get_records_sqlite(conn, table):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    return sorted(result, key=lambda x: x['id'])

def get_records_postgres(conn, table):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM content.{table}")
    rows = cursor.fetchall()
    # Преобразуем UUID в строки
    for row in rows:
        for k, v in row.items():
            if isinstance(v, uuid.UUID):
                row[k] = str(v)
    return sorted(rows, key=lambda x: x['id'])

def remove_ignored_fields(record):
    # Удаляем поля, которые не хотим сравнивать
    for field in FIELDS_TO_IGNORE:
        if field in record:
            del record[field]

@pytest.mark.parametrize("table", TABLES)
def test_data_integrity(sqlite_connection, postgres_connection, table):
    sqlite_records = get_records_sqlite(sqlite_connection, table)
    pg_records = get_records_postgres(postgres_connection, table)

    assert len(sqlite_records) == len(pg_records), f"Количество записей в таблице {table} не совпадает!"

    for sqlite_rec, pg_rec in zip(sqlite_records, pg_records):
        # Удалим игнорируемые поля из обеих записей
        remove_ignored_fields(sqlite_rec)
        remove_ignored_fields(pg_rec)

        # Получаем пересечение ключей
        sqlite_keys = set(sqlite_rec.keys())
        pg_keys = set(pg_rec.keys())
        common_keys = sqlite_keys.intersection(pg_keys)

        for key in common_keys:
            assert sqlite_rec[key] == pg_rec[key], f"Значение поля '{key}' в таблице {table} не совпадает!"
