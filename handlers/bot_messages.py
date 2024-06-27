from aiogram import Router, Bot
from aiogram.types import (
    CallbackQuery,
    InlineQuery,
    InputTextMessageContent,
    InlineQueryResultArticle,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import aiohttp
from bs4 import BeautifulSoup
from config_reader import config
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


router = Router()
bot = Bot(
    token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)


async def fetch_crypto_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://coinmarketcap.com/") as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            data = []
            rows = soup.select(
                'tr[style="cursor:pointer"], tr[style="cursor: pointer;"]'
            )
            for row in rows:
                name_tag = row.select_one(".sc-1c5f2868-3.dhNyQP")
                price_tag = row.select_one(".sc-a093f09c-0.gPTgRa")
                if name_tag and price_tag:
                    name = name_tag.text.strip()
                    price = price_tag.text.strip()
                    data.append((name, price))
            return data


@router.inline_query()
async def inline_query_handler(query: InlineQuery):
    query_text = query.query.upper()

    if not query_text:
        results = [
            InlineQueryResultArticle(
                id="help",
                title="Введите символ криптовалюты",
                input_message_content=InputTextMessageContent(
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
                    InlineQueryResultArticle(
                        id=name,
                        title=f"{name}",
                        description=f"Текущий курс: {price}",
                        input_message_content=InputTextMessageContent(
                            message_text=f"Текущий курс {name}: {price}",
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(
                                        text="Получить курс",
                                        callback_data=f"get_price:{name}",
                                    )
                                ]
                            ]
                        ),
                    )
                )

    await query.answer(results, cache_time=1)


@router.callback_query(lambda c: c.data.startswith("get_price:"))
async def process_callback(callback_query: CallbackQuery):
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
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Обновить", callback_data=f"update:{crypto_name}"
                        )
                    ]
                ]
            ),
        )
    await bot.answer_callback_query(callback_query.id)


@router.callback_query(lambda c: c.data.startswith("update:"))
async def process_update(callback_query: CallbackQuery):
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
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Обновить", callback_data=f"update:{crypto_name}"
                        )
                    ]
                ]
            ),
        )
    await bot.answer_callback_query(callback_query.id)
