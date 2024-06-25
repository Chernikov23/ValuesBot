import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp
from bs4 import BeautifulSoup

API_TOKEN = "7038791110:AAGuYgrntTi2VJCKxNZafpt9Ot2P6YcZIZg"
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def fetch_crypto_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://coinmarketcap.com/") as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            data = []
            rows = soup.select("tr")
            for row in rows:
                name_tag = row.select_one("p.coin-item-symbol")
                price_tag = row.select_one("div.sc-a093f09c-0.gPTgRa")
                if name_tag and price_tag:
                    name = name_tag.text.strip()
                    price = price_tag.text.strip()
                    data.append((name, price))
            return data


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Привет! Введите символ криптовалюты (например, BTC) в inline режиме через @tasks_managerbot."
    )


@dp.inline_query()
async def inline_query_handler(query: types.InlineQuery):
    query_text = query.query.upper()

    if not query_text:
        results = [
            types.InlineQueryResultArticle(
                id="help",
                title="Введите символ криптовалюты",
                input_message_content=types.InputTextMessageContent(
                    message_text="Введите символ криптовалюты, например, BTC или ETH."
                ),
            )
        ]
    else:
        data = await fetch_crypto_data()
        results = []
        for name, price in data:
            if query_text in name:
                results.append(
                    types.InlineQueryResultArticle(
                        id=name,
                        title=f"{name}",
                        description=f"Текущий курс: {price}",
                        input_message_content=types.InputTextMessageContent(
                            message_text=f"Текущий курс {name}: {price}",
                        ),
                        reply_markup=types.InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    types.InlineKeyboardButton(
                                        text="Получить курс",
                                        callback_data=f"get_price:{name}",
                                    )
                                ]
                            ]
                        ),
                    )
                )

    await query.answer(results, cache_time=1)


@dp.callback_query(lambda c: c.data.startswith("get_price:"))
async def process_callback(callback_query: types.CallbackQuery):
    crypto_name = callback_query.data.split(":")[1]
    data = await fetch_crypto_data()
    price = None
    for name, crypto_price in data:
        if name == crypto_name:
            price = crypto_price
            break
    if price:
        await bot.edit_message_text(
            text=f"Текущий курс {crypto_name}: {price}",
            inline_message_id=callback_query.inline_message_id,
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="Обновить", callback_data=f"update:{crypto_name}"
                        )
                    ]
                ]
            ),
        )
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query(lambda c: c.data.startswith("update:"))
async def process_update(callback_query: types.CallbackQuery):
    crypto_name = callback_query.data.split(":")[1]
    data = await fetch_crypto_data()
    price = None
    for name, crypto_price in data:
        if name == crypto_name:
            price = crypto_price
            break
    if price:
        await bot.edit_message_text(
            text=f"Текущий курс {crypto_name}: {price}",
            inline_message_id=callback_query.inline_message_id,
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="Обновить", callback_data=f"update:{crypto_name}"
                        )
                    ]
                ]
            ),
        )
    await bot.answer_callback_query(callback_query.id)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
