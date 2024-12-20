import aiohttp
from secrets import KINOPOISK_TOKEN


async def fetch_movie_data(movie_title):
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=1&query={movie_title}"
    headers = {
        "accept": "application/json",
        "X-API-KEY": KINOPOISK_TOKEN,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                films = await response.json()
                if len(films["docs"]) == 0:
                    print("Фильм не найден на Кинопоиске")
                else:
                    return films["docs"][0]
            else:
                print(
                    f"Ошибка: {response.status}. Не удалось получить данные с Кинопоиска"
                )
