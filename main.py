from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
import os
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import random

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_TOKEN:
    raise ValueError("API не найден")
else:
    print("API токен был успешно инициализирован")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
        random_number = State()
        number = State()


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.reply('Привет, я тг бот, с которым ты можешь поиграть в игру "Угадай число. Напиши /start чтобы начать игру.')

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await Form.random_number.set()
    await bot.send_message(message.chat.id, 'я загадал число от 1 до 10 . Попробуй угадать. (/cancel чтобы остановить игру)')

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='stop', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ok. Игра остановлена. /start чтобы начать заново.')

@dp.message_handler(state=Form.random_number)
async def random_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
       data['random_number'] = random.randint(1, 10)
    await Form.next()
    if int(message.text) == data['random_number']:
        await message.reply('Поздравляю, ты угадал')
        await state.finish()
    elif int(message.text) > data['random_number']:
        await message.reply('Неверно, число младше...')
    elif int(message.text) < data['random_number']:
        await message.reply('Неверно, число старше...')

@dp.message_handler(state=Form.number)
async def answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['number'] = int(message.text)
    if data['number'] == data['random_number']:
        await message.reply('Поздравляю, ты угадал')
        await state.finish()
    elif data['number'] > data['random_number']:
        await message.reply('Неверно, число младше...')
        return answer
    elif data['number'] < data['random_number']:
        await message.reply('Неверно, число старше...')
        return answer

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)