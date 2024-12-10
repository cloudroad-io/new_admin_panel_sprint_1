import sqlite3
import psycopg
from psycopg import ClientCursor, connection as _connection
from psycopg.rows import dict_row
import logging
from dataclasses import dataclass
from typing import List, Optional
from contextlib import contextmanager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("migration.log"),
        logging.StreamHandler()
    ]
)

@dataclass
class Genre:
    id: str
    name: str
    description: str
    created: str
    modified: Optional[str] = None

@dataclass
class FilmWork:
    id: str
    title: str
    description: str
    creation_date: str
    rating: float
    type: str
    created: str
    modified: Optional[str] = None

@dataclass
class Person:
    id: str
    full_name: str
    created: str
    modified: Optional[str] = None

@dataclass
class GenreFilmWork:
    id: str
    genre_id: str
    film_work_id: str
    created: str

@dataclass
class PersonFilmWork:
    id: str
    person_id: str
    film_work_id: str
    role: str
    created: str

BATCH_SIZE = 100  # Размер пакета для загрузки

def fetch_all(cursor, table: str) -> List[dict]:
    cursor.execute(f"SELECT * FROM {table}")
    while True:
        records = cursor.fetchmany(BATCH_SIZE)
        if not records:
            break
        for record in records:
            yield record

def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    try:
        sqlite_cursor = connection.cursor()
        pg_cursor = pg_conn.cursor()
        
        # Загрузка жанров
        genres = fetch_all(sqlite_cursor, 'genre')
        for genre in genres:
            genre_data = Genre(
                id=genre['id'],
                name=genre['name'],
                description=genre['description'],
                created=genre['created_at'],
                modified=genre['updated_at']
            )
            pg_cursor.execute(
                """
                INSERT INTO content.genre (id, name, description, created, modified)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (genre_data.id, genre_data.name, genre_data.description, genre_data.created, genre_data.modified)
            )
        
        # Загрузка фильмов
        films = fetch_all(sqlite_cursor, 'film_work')
        for film in films:
            film_data = FilmWork(
                id=film['id'],
                title=film['title'],
                description=film['description'],
                creation_date=film['creation_date'],
                rating=film['rating'],
                type=film['type'],
                created=film['created_at'],
                modified=film['updated_at']
            )
            pg_cursor.execute(
                """
                INSERT INTO content.film_work (id, title, description, creation_date, rating, type, created, modified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    film_data.id, film_data.title, film_data.description, film_data.creation_date,
                    film_data.rating, film_data.type, film_data.created, film_data.modified
                )
            )
        
        # Загрузка персон
        persons = fetch_all(sqlite_cursor, 'person')
        for person in persons:
            person_data = Person(
                id=person['id'],
                full_name=person['full_name'],
                created=person['created_at'],
                modified=person['updated_at']
            )
            pg_cursor.execute(
                """
                INSERT INTO content.person (id, full_name, created, modified)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (person_data.id, person_data.full_name, person_data.created, person_data.modified)
            )
        
        # Загрузка связи жанров и фильмов
        genre_film_works = fetch_all(sqlite_cursor, 'genre_film_work')
        for gf in genre_film_works:
            gf_data = GenreFilmWork(
                id=gf['id'],
                genre_id=gf['genre_id'],
                film_work_id=gf['film_work_id'],
                created=gf['created_at']
            )
            pg_cursor.execute(
                """
                INSERT INTO content.genre_film_work (id, genre_id, film_work_id, created)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (gf_data.id, gf_data.genre_id, gf_data.film_work_id, gf_data.created)
            )
        
        # Загрузка связи персон и фильмов
        person_film_works = fetch_all(sqlite_cursor, 'person_film_work')
        for pf in person_film_works:
            pf_data = PersonFilmWork(
                id=pf['id'],
                person_id=pf['person_id'],
                film_work_id=pf['film_work_id'],
                role=pf['role'],
                created=pf['created_at']
            )
            pg_cursor.execute(
                """
                INSERT INTO content.person_film_work (id, person_id, film_work_id, role, created)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (pf_data.id, pf_data.person_id, pf_data.film_work_id, pf_data.role, pf_data.created)
            )
        
        pg_conn.commit()
        logging.info("Данные успешно перенесены из SQLite в PostgreSQL.")
    
    except Exception as e:
        pg_conn.rollback()
        logging.error(f"Ошибка при переносе данных: {e}")
        raise
    finally:
        sqlite_cursor.close()
        pg_cursor.close()

if __name__ == '__main__':
    dsl = {
        'dbname': 'movies_database',
        'user': 'app',
        'password': '123qwe',
        'host': '127.0.0.1',
        'port': 5432
    }
    try:
        with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg.connect(
            **dsl, row_factory=dict_row, cursor_factory=ClientCursor
        ) as pg_conn:
            sqlite_conn.row_factory = sqlite3.Row
            load_from_sqlite(sqlite_conn, pg_conn)
    except Exception as e:
        logging.critical(f"Не удалось выполнить миграцию данных: {e}")
