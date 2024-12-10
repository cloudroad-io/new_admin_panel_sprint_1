import psycopg

# Соединение с базой данных PostgreSQL
dsl = {
    'dbname': 'movies_database',
    'user': 'app',
    'password': '123qwe',
    'host': '127.0.0.1',
    'port': 5432
}

# Создание соединения с PostgreSQL
with psycopg.connect(**dsl) as pg_conn:
    with pg_conn.cursor() as cursor:
        # Очистка всех таблиц с учетом внешних ключей и сброса идентификаторов
        cursor.execute("""
            TRUNCATE TABLE content.genre RESTART IDENTITY CASCADE;
            TRUNCATE TABLE content.film_work RESTART IDENTITY CASCADE;
            TRUNCATE TABLE content.person RESTART IDENTITY CASCADE;
            TRUNCATE TABLE content.genre_film_work RESTART IDENTITY CASCADE;
            TRUNCATE TABLE content.person_film_work RESTART IDENTITY CASCADE;
        """)
        pg_conn.commit()

    print("База данных очищена.")
