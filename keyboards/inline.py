from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Фиат", callback_data='fiat'),
            InlineKeyboardButton(text='Криптa', callback_data="crypto")
        ]
    ]
)