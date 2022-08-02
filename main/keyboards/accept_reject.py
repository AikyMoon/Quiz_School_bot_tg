from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

accept = InlineKeyboardButton(text="Принять", callback_data="agree")
reject = InlineKeyboardButton(text="Отклонить", callback_data="disagree")

ar_kb = InlineKeyboardMarkup()
ar_kb.add(accept)
ar_kb.add(reject)
