from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from config import TOKEN

# ------------------ создание бота и диспетчера         ------------------
bot = Bot(TOKEN)
dp = Dispatcher(bot)
