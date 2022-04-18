from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from tockennn import TOKEN
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

# БЛОК С КОНСТАНТАМИ
bot = Bot(token=TOKEN)
num_SCP = ''
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
# Создание кнопок с надписями
button_search = KeyboardButton('Активировать протокол поиска')
button_name_search = KeyboardButton('Поиск SCP')
button_menu = KeyboardButton('Меню')
button_profile = KeyboardButton('Мой профиль')

# Создание кнопочных блоков и присваивание им свойств
greet_search = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_search)
markup_menu = ReplyKeyboardMarkup(resize_keyboard=True).row(button_profile).add(
    button_name_search)
markup_profile = ReplyKeyboardMarkup(resize_keyboard=True).row(button_menu).add(
    button_name_search)


class States(Helper):  # Хранилище состояний
    mode = HelperMode.snake_case
    STATE_1 = ListItem()  # Уровень для ввода номера SCP объекта
    STATE_2 = ListItem()  # Запаска


@dp.message_handler(commands=['t'])  # Команда тестовых вызывов
async def process_hi2_command(message: types.Message):
    await message.reply("Второе - прячем клавиатуру после одного нажатия", reply_markup=greet_search)


@dp.message_handler(commands=['start'])  # Тут все и так понятно)
async def process_hi5_command(message: types.Message):
    await message.reply("Четвертое - расставляем кнопки в ряд", reply_markup=markup_menu)


@dp.message_handler(commands=['help'])  # Тут тоже все и так понятно)
async def process_help_command(message: types.Message):
    await message.reply(
        'Здесь вы можете найти полный архив SCP Foundation\n \n \n/browse *номер объекта* - для поиска статьи об объекте введите \n'
        '/profile - для просмотра профиля введите \n \nПо всем вопросам обращайтесь @vardabomb')


@dp.message_handler(Text(equals="Меню"))  # Выводим блок кнопок меню пользователю
async def with_puree(message: types.Message):
    await message.reply("Вы в главном меню", reply_markup=markup_menu)


@dp.message_handler(Text(equals="Мой профиль"))  # Выводим блок кнопок профиля пользователю
async def with_puree(message: types.Message):
    await message.reply("Это ваш профиль, любуйтесь", reply_markup=markup_profile)


@dp.message_handler(Text(equals="Поиск SCP"))  # Переход в статус получения номера SCP от пользователя
async def with_puree(message: types.Message):
    await message.reply("Введите номер SCP", reply_markup=greet_search)
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[0])  # Вот тут включается статус 1


@dp.message_handler(Text(equals="Активировать протокол поиска"),
                    state=['state_1'])  # После нажатия этой кнопки должна появиться информация об SCP
async def with_puree(message: types.Message):
    global num_SCP
    if num_SCP:  # Проверка на то вводил ли пользователь вообще номер SCP
        await message.reply(f"Я отчаянно пытаюсь найти информацию про SCP {num_SCP}", reply_markup=markup_menu)
        state = dp.current_state(user=message.from_user.id)
        await state.reset_state()
        num_SCP = ''
    else:
        await message.reply('Ты не указали номер SCP')


@dp.message_handler()  # Заглушка для ввода неправильных сообщений пользователя в обычном статусе
async def echo_message(message: types.Message):
    await message.reply("Ошибка ввода!\nЕсли вам нужна помощь пропишите /help")


@dp.message_handler(state=['state_1'])  # Заглушка для ввода неправильных сообщений пользователя в 1 статусе
async def with_puree(message: types.Message):
    global num_SCP
    if message['text'].isdigit():
        num_SCP = message['text']
        await message.reply("Верный ввод")
    else:
        await message.reply("Ошибка ввода!\nВведите номер SCP без лишних знаков")


@dp.message_handler(state=States.STATE_2)  # Заглушка для ввода неправильных сообщений пользователя в 2 статусе
async def echo_message(msg: types.Message):
    await msg.reply('Второй!', reply=False)


async def shutdown(dispatcher: Dispatcher):  # Функция закрытия соединения с хранилищем состояний
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp)
    executor.start_polling(dp, on_shutdown=shutdown)

"""@dp.message_handler(content_types=types.ContentType.TEXT)
async def with_puree(message: types.Message):
    global num_SCP
    if message['text'].isdigit():
        num_SCP = message['text']
    else:
        await message.reply("Неверный ввод, попробуйте повторить")"""

"""@dp.message_handler(content_types=['text'])
async def echo_message(msg: types.Message):
    print(msg.text.lower())
    if msg.text.lower() == 'мой профиль':
        await msg.reply("Лох без профиля)")
    elif msg.text.lower() == 'поиск scp':
        await msg.reply("Ну давай, ищи теперь, бака")
    elif msg.text.lower() == 'меню':
        await msg.reply("Чел, ты и так в меню")
    else:
        await msg.answer('Не понимаю, что это значит.')
"""
