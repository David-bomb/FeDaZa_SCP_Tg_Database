from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from tockennn import TOKEN
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
button_search = KeyboardButton('Поиск SCP')
button_menu = KeyboardButton('Меню')
button_profile = KeyboardButton('Мой профиль')
# keyboards.py

greet_kb1 = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_menu)

greet_kb2 = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_profile)

greet_kb3 = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_search)

markup_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_profile).add(button_search).add(button_menu)


@dp.message_handler(commands=['t'])
async def process_hi2_command(msg: types.Message):
    await msg.reply("Второе - прячем клавиатуру после одного нажатия", reply_markup=greet_kb2)


@dp.message_handler(commands=['m'])
async def process_hi5_command(msg: types.Message):
    await msg.reply("Четвертое - расставляем кнопки в ряд", reply_markup=markup_menu)

@dp.message_handler(content_types=['text'])
async def echo_message(msg: types.Message):
    print(msg.text.lower())
    if msg.text.lower() == 'мой профиль':
        await msg.reply("Лох без профиля)")
    elif msg.text.lower() == 'поиск SCP':
        await msg.reply("Ну давай, ищи теперь, бака")
    elif msg.text.lower() == 'меню':
        await msg.reply("Чел, ты и так в меню")
    else:
        await msg.answer('Не понимаю, что это значит.')

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")



if __name__ == '__main__':
    executor.start_polling(dp)