import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from video_search import search_vk_video
from kinopoisk_search import fetch_movie_data
from database import init_db, log_search, get_search_history, get_film_stats
from secrets import TG_TOKEN, VK_TOKEN


dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(
        f"""
        Привет, {message.from_user.full_name}! 👋

        Я твой виртуальный помощник в мире кино. 🎬✨

        Напиши мне название фильма, а я пришлю ссылку для просмотра.

        Например: *Александр Невский*

        *Команды:*
        📜 /help - помощь
        🔍 /history - история поисковых запросов
        📊 /stats - статистика просмотров
        """,
        parse_mode="Markdown",
    )


@dp.message(Command("help"))
async def help_command(message):
    await message.answer(
        """
        *Команды:*

        📜 /help - помощь
        🔍 /history - история поисковых запросов
        📊 /stats - статистика просмотров

        _Для поиска фильма напишите его название._
        Например: *Александр Невский*
        """,
        parse_mode="Markdown",
    )


@dp.message(Command("history"))
async def history_command(message: types.Message):
    user_id = message.from_user.id
    history = await get_search_history(user_id)

    if not history:
        await message.answer("История поиска пуста.")
        return

    response = "<b>История поиска:</b>\n"

    for film_title, timestamp in history:
        response += f"⏱️ {timestamp}      🎬 <i>{film_title}</i>\n"

    await message.answer(response, parse_mode="HTML")


@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    user_id = message.from_user.id
    stats = await get_film_stats(user_id)

    if not stats:
        await message.answer(
            "🔍 Ваша статистика пуста. Возможно, вы еще не посмотрели ни одного фильма."
        )
        return

    response = "🎬 <b>Статистика ваших фильмов:</b>\n\n"
    for film_title, count in stats:
        response += f"📽️ <i>{film_title}</i>: {count} раз(а)\n"

    await message.answer(response, parse_mode="HTML")


@dp.message()
async def movie_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    """
    film = await fetch_movie_data(message.text)
    if film is None:
        return

    title = film.get("name", "")
    year = film.get("year", "Неизвестный год")
    genres = ", ".join(genre["name"] for genre in film.get("genres", []))
    countries = ", ".join(country["name"]
                          for country in film.get("countries", []))
    rating_kp = film["rating"].get("kp", "Нет рейтинга")
    rating_imdb = film["rating"].get("imdb", "Нет рейтинга")
    description = film.get("shortDescription", "Нет описания")

    search_query = message.text + " " + str(year)
    link = await search_vk_video(search_query, VK_TOKEN)

    message_text = (
        f"🎬 <b>{title}</b> ({year})\n"
        f"🌍 Страна: {countries}\n"
        f"🎭 Жанры: {genres}\n"
        f"⭐ Рейтинг КиноПоиск: {rating_kp}\n"
        f"⭐ Рейтинг IMDb: {rating_imdb}\n\n"
    )

    if description != "":
        message_text += f"📝 <i>{description}</i>\n\n"

    message_text += f"🔗 <a href='{link}'>Смотреть фильм</a>"

    photo_url = film["poster"]["url"]
    await message.answer_photo(photo=photo_url, caption=message_text, parse_mode="HTML")

    await log_search(message.from_user.id, title)


async def main() -> None:
    await init_db()
    bot = Bot(
        token=TG_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
