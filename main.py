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


@dp.message_handler(commands=['start'])  # Просто приветствие
async def send_welcome(msg: types.Message):
    await msg.reply(f'Привет, меня зовут ScpArchive. Приятно познакомиться, {msg.from_user.first_name}!')
    cur = conn.cursor()
    if not cur.execute(
            f'''SELECT * FROM users WHERE userid = {msg.from_user.id}''').fetchall():  # регистрация пользователя, если он еще не занесён в БД
        sql = '''INSERT INTO users(userid, username, name,  level, number_of_requests, number_of_bugs) VALUES(?, ?, ?, ?, ?, ?)'''
        data_tuple = (msg.from_user.id, msg.from_user.username, msg.from_user.first_name, 0, 0, 0)
        cur.execute(sql, data_tuple)
        conn.commit()


@dp.message_handler(commands=['help'])
async def helper(msg: types.Message):  # Создание функции help
    await msg.reply('''Пока что у меня мало функций, но я уже могу кидать ссылку на статью об обьекте, если
    вы отправите команду /browse *название объекта*, где название объекта пишется как 001''')


@dp.message_handler(commands=['browse'])  # TODO Это скорее демонстративная команда, мы не будем отправлять ссылки,
async def browse(msg: types.Message):  # TODO а будем отправлять инфу в сообщениях, описание, картинка и тд.
    argument = msg.get_args()  # Аргумент, то есть название объекта
    if argument:  # проверяем, ввели ли аргумент
        try:  # Пытаемся найти этот объект, в противном случае пишем что не нашли
            info = get_content(f'http://scpfoundation.net/scp-{argument}', id='page-title') + '\n' + \
                   get_content(f'http://scpfoundation.net/scp-{argument}')  # Создаём ответ бота
            if len(info) > 4096:  # Если он слишком большой, то мы делим его на несколько сообщений для обхода ограничений Telegram
                for x in range(0, len(info), 4096):
                    await bot.send_message(msg.chat.id, info[x:x + 4096])
            else:
                await bot.send_message(msg.chat.id, info)
            cur = conn.cursor()
            cur.execute(
                f'''UPDATE users SET number_of_requests = number_of_requests + 1 WHERE userid = {msg.from_user.id}''')
            conn.commit()  # Прибавляем 1 к кол-ву запросов, для отслеживания прогресса уровня
        except Exception as e:  # Запись ошибки в лог, если пользователь столкнулся с ошибкой разряда ERROR или FATAL, возможно появление логов от самого aiogram
            logging.error(' '.join([str(msg.from_user.id), msg.from_user.username, str(e)]))
            cur = conn.cursor()
            cur.execute(  # Фиксирование ошибки и прикрепление ошибки к пользователю, для возможного опроса в будущем
                f'''UPDATE users SET number_of_bugs = number_of_bugs + 1 WHERE userid = {msg.from_user.id}''')
            conn.commit()
            await msg.reply('Я всё обыскал, нигде не нашёл того, чего вы хотели, или же я допустил ошибку.')
    else:
        await msg.reply('Я не думаю что я смогу найти нужный объект, если вы не укажете его название')


@dp.message_handler(content_types=['text'])  # Шаблон приема обычного сообщения
async def get_text_messages(msg: types.Message):
    if msg.text.lower() == 'привет' or msg.text.lower() == 'здравствуй' or msg.text.lower() == 'приветствую':
        await msg.answer(f'Привет, {msg.from_user.first_name}')
    else:
        await msg.answer('Не понимаю, что это значит.')


if __name__ == '__main__':
    executor.start_polling(dp)
