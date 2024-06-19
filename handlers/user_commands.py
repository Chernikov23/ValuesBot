from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram import Router
from keyboards import inline

router = Router()

@router.message(CommandStart())
async def start(msg: Message):
    await msg.answer("Hello!!!", reply_markup=inline.main)