import os
from os.path import dirname, join
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import sqlite3
from dotenv import load_dotenv
from utilites import get_content
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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
change_photo = False  # TODO СМЕНИТЬ РЕАЛИЗАЦИЮ МЕХАНИКИ ЧЕРЕЗ users.db


@dp.message_handler(commands=['start'])  # Просто приветствие
async def send_welcome(msg: types.Message):
    global change_photo
    change_photo = False

    await msg.reply(f'Hello, my name is ScpArchive. Nice to meet you, {msg.from_user.first_name}!')
    cur = conn.cursor()
    date_time_str = datetime.now()
    if not cur.execute(
            f'''SELECT * FROM users WHERE userid = {msg.from_user.id}''').fetchall():  # регистрация пользователя, если он еще не занесён в БД
        sql = '''INSERT INTO users(userid, username, name,  level, number_of_requests, number_of_bugs, date_of_registration, 
        photo, nickname, language) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        data_tuple = (msg.from_user.id, msg.from_user.username, msg.from_user.first_name, 1, 0, 0,
                      date_time_str.replace(microsecond=0),
                      'AgACAgIAAxkBAAIDd2JcUPUnu4OrqO59i9-M4FSRz3CmAALauDEbwQLoSo_J1EadLNMAAQEAAwIAA3MAAyQE',
                      msg.from_user.username, 'EN')
        cur.execute(sql, data_tuple)
        conn.commit()


@dp.message_handler(commands=['help'])
async def helper(msg: types.Message):  # Создание функции help
    cur = conn.cursor()
    language = cur.execute(f'''SELECT language FROM users WHERE userid = {msg.from_user.id}''').fetchall()[0][0]
    language_text = {
        'RU': 'Здесь вы можете найти полный архив SCP Foundation\n \n \n/browse *номер объекта* - для поиска статьи об объекте \n'
              '/profile - для просмотра профиля \n/change_language *language* - изменить язык (доступные языки RU, EN)\nПо всем вопросам обращайтесь @vardabomb',
        'EN': 'Here you can find the full SCP Foundation archive\n \n \n/browse *object number* - to search for an article about the object \n'
              '/profile - to view the profile \n/change_language *language* - to change the language (available languages RU, EN)\n \n'
              'Any questions contact @vardabomb'
    }
    global change_photo
    change_photo = False
    await msg.reply(language_text[language])


@dp.message_handler(commands=['change_language'])
async def helper(msg: types.Message):
    argument = msg.get_args()
    if argument in ('RU', 'EN'):
        cur = conn.cursor()
        cur.execute(f"""UPDATE users SET language = '{argument}' WHERE userid = {msg.from_user.id}""")
        language = cur.execute(f'''SELECT language FROM users WHERE userid = {msg.from_user.id}''').fetchall()[0][0]
        succesfully = {
            'RU': 'Успешно',
            'EN': 'Successfully'
        }
        conn.commit()
        await msg.answer(text=succesfully[language] + '👍')


@dp.message_handler(commands=['profile'])
async def profile(msg: types.Message):  # создание функции профиля
    global change_photo
    change_photo = False
    cur = conn.cursor()
    profile = cur.execute(f'''SELECT * FROM users WHERE userid = {msg.from_user.id}''').fetchall()
    conn.commit()
    cur = conn.cursor()
    language = cur.execute(f'''SELECT language FROM users WHERE userid = {msg.from_user.id}''').fetchall()[0][0]
    language_text = {
        'RU': f'Имя: {profile[0][8]}.\nДата регистрации: {profile[0][6]}.\nКоличество запросов: {profile[0][4]}.\n'
              f'Уровень {profile[0][3]}.\n \nЧтобы повысить уровень делайте больше запросов\n \nВозможности:\n'
              f'/edit_nickname - изменить имя.\n/edit_photo - изменить фотографию',
        'EN': f'Name: {profile[0][8]}.\nRegistration Date: {profile[0][6]}.\nNumber of requests: {profile[0][4]}.\n'
              f'Level {profile[0][3]}.\n \nMake more requests to level up\n \nFeatures:\n'
              f'/edit_nickname *new nickname* - to change name.\n/edit_photo - to change photo'
    }
    await bot.send_photo(msg.chat.id, str(profile[0][7]))  # Вывод фото профиля и его статистики
    await bot.send_message(msg.chat.id, language_text[language])


@dp.message_handler(commands=['edit_photo'])
async def edit_photo(msg: types.Message):  # Функция смены фото профиля в БД бота
    global change_photo
    change_photo = True
    cur = conn.cursor()
    language = cur.execute(f'''SELECT language FROM users WHERE userid = {msg.from_user.id}''').fetchall()[0][0]
    language_text = {
        'RU': 'Пришлите новую фотографию:',
        'EN': 'Submit a new photo:'
    }
    await bot.send_message(msg.chat.id, language_text[language])


@dp.message_handler(commands=['edit_nickname'])
async def edit_nickname(msg: types.Message):  # Смена никнейма в профиле, но при этом основной username сохраняется
    global change_photo
    change_photo = False
    argument = msg.get_args()
    if argument:
        cur = conn.cursor()
        argument = msg.get_args()
        language = cur.execute(f'''SELECT language FROM users WHERE userid = {msg.from_user.id}''').fetchall()[0][0]
        succesfully = {
            'RU': 'Успешно',
            'EN': 'Successfully'
        }
        cur.execute(f"""UPDATE users SET nickname = '{argument}' WHERE userid = {msg.from_user.id}""")
        conn.commit()
        await msg.answer(text=succesfully[language] + '👍')


@dp.message_handler(content_types=[types.ContentType.PHOTO])
async def edit_photo(msg: types.Message):  # Функция получения фото
    global change_photo
    if change_photo:
        document_id = msg.photo[0].file_id
        file_info = await bot.get_file(document_id)
        cur = conn.cursor()
        language = cur.execute(f'''SELECT language FROM users WHERE userid = {msg.from_user.id}''').fetchall()[0][0]
        succesfully = {
            'RU': 'Успешно',
            'EN': 'Successfully'
        }
        cur.execute(
            f"""UPDATE users SET photo = '{file_info.file_id}' WHERE userid = {msg.from_user.id}""")  # Добавление фото в БД
        conn.commit()
        change_photo = False
        await msg.answer(text=succesfully[language] + '👍')
    else:
        cur = conn.cursor()
        language = cur.execute(f'''SELECT language FROM users WHERE userid = {msg.from_user.id}''').fetchall()[0][0]
        language_text = {
            'RU': 'Красивая фотография, но что вы хотите?',
            'EN': 'Very nice photo, but what do you want?'
        }
        await bot.send_message(msg.chat.id, language_text[language])


@dp.message_handler(commands=['browse'])  # Функция запроса scp объекта, основная функция бота
async def browse(msg: types.Message):
    global change_photo
    change_photo = False
    cur = conn.cursor()
    language = cur.execute(f'''SELECT language FROM users WHERE userid = {msg.from_user.id}''').fetchall()[0][0]
    argument = msg.get_args()  # Аргумент, то есть название объекта
    if len(argument) < 3:
        argument = '0' * (3 - len(argument)) + argument
    if argument:  # проверяем, ввели ли аргумент
        try:  # Пытаемся найти этот объект, в противном случае пишем что не нашли
            language_text = {
                'RU': f'http://scp-ru.wikidot.com/scp-{argument}',
                'EN': f'https://scp-wiki.wikidot.com/scp-{argument}'
            }
            info = get_content(language_text[language], id='page-title') + '\n' + \
                   get_content(language_text[language])  # Создаём ответ бота
            text = requests.get(language_text[language]).text
            try:
                if language == 'RU':
                    await bot.send_photo(msg.chat.id,
                                         BeautifulSoup(text, 'html.parser').find(class_="rimg").find(
                                             class_="image").get(
                                             'src'))
                elif language == 'EN':
                    await bot.send_photo(msg.chat.id,
                                         BeautifulSoup(text, 'html.parser').find(
                                             class_="scp-image-block block-right").find(class_="image").get('src'))
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
            # Перебор уровней и кол-ва запросов для установления новых уровней
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
        except Exception as e:  # Запись ошибки в лог, если пользователь столкнулся с ошибкой разряда ERROR или FATAL, возможно появление логов от самого aiogram
            logging.error(' '.join([str(msg.from_user.id), msg.from_user.username, str(e)]))
            cur = conn.cursor()
            cur.execute(  # Фиксирование ошибки и прикрепление ошибки к пользователю, для возможного опроса в будущем
                f'''UPDATE users SET number_of_bugs = number_of_bugs + 1 WHERE userid = {msg.from_user.id}''')
            conn.commit()
            language_error = {
                'RU': 'Я всё обыскал, нигде не нашёл того, чего вы хотели, или же я допустил ошибку.',
                'EN': '''I searched everywhere, didn't find what you wanted anywhere, or I made a mistake.'''
            }
            await msg.reply(language_error[language])
    else:
        language_error1 = {
            'RU': 'Я всё обыскал, нигде не нашёл того, чего вы хотели, или же я допустил ошибку.',
            'EN': '''I searched everywhere, didn't find what you wanted anywhere, or I made a mistake.'''
        }
        await msg.reply(language_error1[language])


@dp.message_handler(content_types=[types.ContentType.ANY])  # Шаблон приема обычного сообщения
async def get_text_messages(msg: types.Message):
    global change_photo
    change_photo = False
    cur = conn.cursor()
    language = cur.execute(f'''SELECT language FROM users WHERE userid = {msg.from_user.id}''').fetchall()[0][0]
    language_text = {
        'RU': f'{msg.from_user.first_name}, архив не может обработать данный тип информации, используйте команды.',
        'EN': f'{msg.from_user.first_name}, cannot archive this type of information, tag the command.'
    }
    await msg.reply(language_text[language])


if __name__ == '__main__':
    executor.start_polling(dp)
