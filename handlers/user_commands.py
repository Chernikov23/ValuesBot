from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router

router = Router()

@router.message(CommandStart())
async def start(msg: Message):
    await msg.answer("Привет! Я бот, отображающий курсы фиатных и криптовалют. Чтобы пользоваться мною, введите в любом чате @<имя бота> (символ валюты, например TON, BTC, ETH)")
