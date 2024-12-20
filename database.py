import aiosqlite


async def init_db():
    async with aiosqlite.connect("movies.db") as conn:
        cursor = await conn.cursor()

        # Создание таблицы для хранения истории запросов
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS search_history (
                user_id INTEGER,
                film_title TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Создание таблицы для хранения статистики фильмов
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS film_stats (
                film_title TEXT,
                user_id INTEGER,
                count INTEGER DEFAULT 0,
                PRIMARY KEY (film_title, user_id)
            )
        """
        )

        await conn.commit()


async def log_search(user_id, film_title):
    async with aiosqlite.connect("movies.db") as conn:
        cursor = await conn.cursor()

        await cursor.execute(
            "INSERT INTO search_history (user_id, film_title) VALUES (?, ?)",
            (user_id, film_title),
        )

        await cursor.execute(
            """
            INSERT INTO film_stats (film_title, user_id, count) VALUES (?, ?, 1)
            ON CONFLICT(film_title, user_id) DO UPDATE SET count = count + 1
        """,
            (film_title, user_id),
        )

        await conn.commit()


async def get_search_history(user_id):
    async with aiosqlite.connect("movies.db") as conn:
        cursor = await conn.cursor()

        await cursor.execute(
            "SELECT film_title, timestamp FROM search_history WHERE user_id = ?",
            (user_id,),
        )
        history = await cursor.fetchall()

        return history


async def get_film_stats(user_id):
    async with aiosqlite.connect("movies.db") as conn:
        cursor = await conn.cursor()

        await cursor.execute(
            "SELECT film_title, count FROM film_stats WHERE user_id = ?", (user_id,)
        )
        stats = await cursor.fetchall()

        return stats
