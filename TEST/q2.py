import os
from os.path import dirname, join
import sqlite3
from dotenv import load_dotenv
from utilites import get_content
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

# Создание бота, импорт токена из отдельного файла .env, установка логирования и соединения с БД
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TOKEN = os.environ.get('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
conn = sqlite3.connect('users.db')
logging.basicConfig(
    filename='errors.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.ERROR
)
global change_photo
change_photo = False

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


@dp.message_handler(commands=['start'])  # Просто приветствие
async def send_welcome(msg: types.Message):
    global change_photo
    change_photo = False
    await msg.reply(f'Привет, меня зовут ScpArchive. Приятно познакомиться, {msg.from_user.first_name}!', reply_markup=markup_menu)
    cur = conn.cursor()
    date_time_str = datetime.now()
    if not cur.execute(
            f'''SELECT * FROM users WHERE userid = {msg.from_user.id}''').fetchall():  # регистрация пользователя, если он еще не занесён в БД
        sql = '''INSERT INTO users(userid, username, name,  level, number_of_requests, number_of_bugs, date_of_registration, 
        photo, nickname) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        data_tuple = (msg.from_user.id, msg.from_user.username, msg.from_user.first_name, 1, 0, 0,
                      date_time_str.replace(microsecond=0),
                      'AgACAgIAAxkBAAIDd2JcUPUnu4OrqO59i9-M4FSRz3CmAALauDEbwQLoSo_J1EadLNMAAQEAAwIAA3MAAyQE',
                      msg.from_user.username)
        cur.execute(sql, data_tuple)
        conn.commit()


@dp.message_handler(commands=['help'])
async def helper(msg: types.Message):  # Создание функции help
    global change_photo
    change_photo = False
    await msg.reply(
        'Здесь вы можете найти полный архив SCP Foundation\n \n \n/browse *номер объекта* - для поиска статьи об объекте введите \n'
        '/profile - для просмотра профиля введите \n \nПо всем вопросам обращайтесь @vardabomb')


@dp.message_handler(Text(equals="Мой профиль"))  # Выводим блок кнопок профиля пользователю
async def with_puree(msg: types.Message):
    global change_photo
    await msg.reply("Это ваш профиль, любуйтесь", reply_markup=markup_profile)
    change_photo = False
    cur = conn.cursor()
    profile = cur.execute(f'''SELECT * FROM users WHERE userid = {msg.from_user.id}''').fetchall()
    conn.commit()
    await bot.send_photo(msg.chat.id, str(profile[0][7]))
    await bot.send_message(msg.chat.id,
                           f'Имя: {profile[0][8]}.\nДата регистрации: {profile[0][6]}.\nКоличество запросов: {profile[0][4]}.\n'
                           f'Уровень {profile[0][3]}.\n \nЧтобы повысить уровень делайте больше запросов\n \nВозможности:\n'
                           f'/edit_nickname - изменить имя.\n/edit_photo - изменить фотографию')


@dp.message_handler(commands=['edit_photo'])
async def edit_photo(msg: types.Message):
    global change_photo
    change_photo = True
    await bot.send_message(msg.chat.id, "Пришлите новую фотографию:")


@dp.message_handler(commands=['edit_nickname'])
async def edit_nickname(msg: types.Message):
    global change_photo
    change_photo = False
    argument = msg.get_args()
    if argument:
        cur = conn.cursor()
        cur.execute(f"""UPDATE users SET nickname = '{argument}' WHERE userid = {msg.from_user.id}""")
        conn.commit()


@dp.message_handler(content_types=[types.ContentType.PHOTO])
async def edit_photo(msg: types.Message):
    global change_photo
    if change_photo:
        document_id = msg.photo[0].file_id
        file_info = await bot.get_file(document_id)
        cur = conn.cursor()
        cur.execute(f"""UPDATE users SET photo = '{file_info.file_id}' WHERE userid = {msg.from_user.id}""")
        conn.commit()
        change_photo = False
    else:
        await bot.send_message(msg.chat.id, "Красивая фотография, но что вы хотите?")


@dp.message_handler(Text(equals="Меню"))  # Выводим блок кнопок меню пользователю
async def with_puree(message: types.Message):
    await message.reply("Вы в главном меню", reply_markup=markup_menu)


@dp.message_handler(Text(equals="Поиск SCP"))  # Переход в статус получения номера SCP от пользователя
async def with_puree(message: types.Message):
    await message.reply("Введите номер SCP", reply_markup=greet_search)
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[0])  # Вот тут включается статус 1


@dp.message_handler(Text(equals="Активировать протокол поиска"),
                    state=['state_1'])  # После нажатия этой кнопки должна появиться информация об SCP
async def with_puree(msg: types.Message):
    global num_SCP
    if num_SCP:  # Проверка на то вводил ли пользователь вообще номер SCP
        await msg.reply(f"Я отчаянно пытаюсь найти информацию про SCP {num_SCP}", reply_markup=markup_menu)
        global change_photo
        change_photo = False
        argument = num_SCP  # Аргумент, то есть название объекта
        if len(argument) < 3:
            argument = '0' * (3 - len(argument)) + argument
        try:  # Пытаемся найти этот объект, в противном случае пишем что не нашли
            info = get_content(f'http://scp-ru.wikidot.com/scp-{argument}', id='page-title') + '\n' + \
                   get_content(f'http://scp-ru.wikidot.com/scp-{argument}')  # Создаём ответ бота
            text = requests.get(f'http://scp-ru.wikidot.com/scp-{argument}').text
            try:
                await bot.send_photo(msg.chat.id,
                                     BeautifulSoup(text, 'html.parser').find(class_="rimg").find(class_="image").get(
                                         'src'))
            except:
                await bot.send_photo(msg.chat.id,
                                     'AgACAgIAAxkBAAIDd2JcUPUnu4OrqO59i9-M4FSRz3CmAALauDEbwQLoSo_J1EadLNMAAQEAAwIAA3MAAyQE')
            if len(
                    info) > 4096:  # Если он слишком большой, то мы делим его на несколько сообщений для обхода ограничений Telegram
                for x in range(0, len(info), 4096):
                    await bot.send_message(msg.chat.id, info[x:x + 4096])
            else:
                await bot.send_message(msg.chat.id, info)
            cur = conn.cursor()
            cur.execute(
                f'''UPDATE users SET number_of_requests = number_of_requests + 1 WHERE userid = {msg.from_user.id}''')
            requests_n = cur.execute(
                f'''SELECT number_of_requests FROM users WHERE userid = {msg.from_user.id}''').fetchall()
            lvl = cur.execute(f'''SELECT level FROM users WHERE userid = {msg.from_user.id}''').fetchall()
            requests_n = int(requests_n[0][0])
            lvl = int(lvl[0][0])
            if lvl < 2 and requests_n >= 125:
                cur.execute(
                    f"""UPDATE users SET level = '2' WHERE userid = {msg.from_user.id}""")
            elif lvl < 3 and requests_n >= 225:
                cur.execute(
                    f"""UPDATE users SET level = '3' WHERE userid = {msg.from_user.id}""")
            elif lvl < 4 and requests_n >= 350:
                cur.execute(
                    f"""UPDATE users SET level = '4' WHERE userid = {msg.from_user.id}""")
            elif lvl < 5 and requests_n >= 500:
                cur.execute(
                    f"""UPDATE users SET level = '5' WHERE userid = {msg.from_user.id}""")
            elif lvl < 6 and requests_n >= 675:
                cur.execute(
                    f"""UPDATE users SET level = '6' WHERE userid = {msg.from_user.id}""")
            elif requests_n >= 900:
                cur.execute(
                    f"""UPDATE users SET level = '7' WHERE userid = {msg.from_user.id}""")
            conn.commit()  # Прибавляем 1 к кол-ву запросов, для отслеживания прогресса уровня
            state = dp.current_state(user=msg.from_user.id)
            await state.reset_state()
            num_SCP = ''
        except Exception as e:  # Запись ошибки в лог, если пользователь столкнулся с ошибкой разряда ERROR или FATAL, возможно появление логов от самого aiogram
            logging.error(' '.join([str(msg.from_user.id), msg.from_user.username, str(e)]))
            cur = conn.cursor()
            cur.execute(  # Фиксирование ошибки и прикрепление ошибки к пользователю, для возможного опроса в будущем
                f'''UPDATE users SET number_of_bugs = number_of_bugs + 1 WHERE userid = {msg.from_user.id}''')
            conn.commit()
            await msg.reply('Я всё обыскал, нигде не нашёл того, чего вы хотели, или же я допустил ошибку.')

            state = dp.current_state(user=msg.from_user.id)
            await state.reset_state()
            num_SCP = ''
    else:
        await msg.reply('Ты не указали номер SCP')


@dp.message_handler(content_types=[types.ContentType.TEXT])  # Шаблон приема обычного сообщения
async def get_text_messages(msg: types.Message):
    global change_photo
    change_photo = False
    await msg.reply(
        f'{msg.from_user.first_name}, архив не может обработать данный тип информации, используйте команды.')


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
