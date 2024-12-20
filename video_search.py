import aiohttp


async def search_vk_video(video_title, access_token):
    # URL для поиска видео в ВКонтакте
    search_url = "https://api.vk.com/method/video.search"

    params = {
        "q": video_title,  # Название видео для поиска
        "access_token": access_token,  # Токен доступа
        "v": "5.131",  # Версия API
        "count": 1,  # Количество результатов
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(search_url, params=params) as response:
            if response.status == 200:
                data = await response.json()

                # Проверяем наличие ошибок в ответе
                if "error" in data:
                    print(f"Ошибка: {data['error']['error_msg']}")
                    return None

                # Извлекаем информацию о видео
                items = data.get("response", {}).get("items", [])
                if items:
                    video = items[0]
                    video_url = f"https://vk.com/video{video['owner_id']}_{video['id']}"
                    return video_url
                else:
                    print("Видео не найдено.")
                    return None
            else:
                print(f"Ошибка запроса: {response.status}")
                return None
