import os
from os.path import dirname, join
import sqlite3
from dotenv import load_dotenv
import logging
from datetime import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from language import languages
import utilites as u

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
num_SCP = ''
# Создание кнопок с надписями
button_search = KeyboardButton('Активировать протокол поиска')
button_name_search = KeyboardButton('Поиск SCP')
button_menu = KeyboardButton('Меню')
button_profile = KeyboardButton('Мой профиль')

# Создание кнопочных блоков и присваивание им свойств
return_profile = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_profile)
greet_search = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).row(button_menu).add(button_search)
markup_menu = ReplyKeyboardMarkup(resize_keyboard=True).row(button_profile).add(
    button_name_search)
markup_profile = ReplyKeyboardMarkup(resize_keyboard=True).row(button_menu).add(
    button_name_search)


class States(Helper):
    mode = HelperMode.snake_case
    STATE1_WORK = ListItem()  # Уровень для работы с ботом
    STATE2_SEARCH = ListItem()  # Уровень для ввода номера SCP объекта

    STATE4_PHOTO = ListItem()  # Уровень для смены фото
    STATE5_NAME = ListItem()  # Уровень для смены ника и фото


@dp.message_handler(commands=['start'])  # Первый старт, регистрирует пользователя и выдает статус
async def send_welcome(msg: types.Message):
    state = dp.current_state(user=msg.from_user.id)
    print(States.all())
    await state.set_state(States.all()[0])

    await msg.reply(f'Здравствуйте, {msg.from_user.first_name}. Архив готов к работе.',
                    reply_markup=markup_menu)
    cur = conn.cursor()
    date_time_str = datetime.now()
    if not cur.execute(
            f'''SELECT * FROM users WHERE userid = {msg.from_user.id}''').fetchall():  # регистрация пользователя, если он еще не занесён в БД
        sql = '''INSERT INTO users(userid, username, name,  level, number_of_requests, number_of_bugs, date_of_registration, 
        photo, nickname, language, last_scp) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        data_tuple = (msg.from_user.id, msg.from_user.username, msg.from_user.first_name, 1, 0, 0,
                      date_time_str.replace(microsecond=0),
                      'AgACAgIAAxkBAAIDd2JcUPUnu4OrqO59i9-M4FSRz3CmAALauDEbwQLoSo_J1EadLNMAAQEAAwIAA3MAAyQE', msg.from_user.username,
                      'RU', 0)
        cur.execute(sql, data_tuple)
        conn.commit()


@dp.message_handler(commands=['start'], state=States.all())  # Перезагрузка статуса бота
async def send_welcome(msg: types.Message):
    state = dp.current_state(user=msg.from_user.id)
    await state.set_state(States.all()[0])
    await msg.reply(f'{msg.from_user.first_name}, поисковик перепущен.',
                    reply_markup=markup_menu)


@dp.message_handler(commands=['help'], state=States.all())
async def helper(msg: types.Message):  # Создание функции help
    state = dp.current_state(user=msg.from_user.id)
    await state.set_state(States.all()[0])
    await msg.reply(
        'Здесь вы можете найти полный архив SCP Foundation\n \n \n Активируйте поиск scp для поиска статьи об объекте. \n'
        'Мой профиль - для просмотра профиля \n \nПо всем вопросам обращайтесь @vardabomb')


@dp.message_handler(commands=['change_language'], state=States.all())
async def lang(msg: types.Message):
    print(1)
    argument = msg.get_args()
    cur = conn.cursor()
    language = cur.execute(f'''SELECT language FROM users WHERE userid = {msg.from_user.id}''').fetchall()[0][0]
    print(2)
    if argument in ('RU', 'EN'):
        print(3)
        print(argument)
        print(msg.from_user.id)
        print(f"""UPDATE users SET language = '{argument}' WHERE userid = {msg.from_user.id}""")
        cur.execute(f"""UPDATE users SET language = '{argument}' WHERE userid = {msg.from_user.id}""")
        conn.commit()
        print(4)
        print(5)
        await msg.answer(text=languages['Successfully'][language] + '👍')
        print(6)
    else:
        await msg.answer(languages['lang_no_arg'][language])


@dp.callback_query_handler(Text(startswith="search_"),
                           state=States.STATE2_SEARCH)  # Обработка запросов инлайн кнопок поиска SCP
async def callbacks_num(call: types.CallbackQuery):
    cur = conn.cursor()
    num_SCP = cur.execute(f'''SELECT last_scp FROM users WHERE userid = {call.from_user.id}''').fetchall()[0][0]
    action = call.data.split("_")[1]

    if action == "front":  # Триггер нажатия на кнопку просмотра следующего SCP
        print('Вперед')
        info = u.browse(f'{int(num_SCP) + 1}', call.message.chat.id)  # TODO ERROR
        print(1)
        print(info['text'])
        await bot.send_photo(call.message.chat.id, info['img'])
        for x in range(0, len(info['text']), 4096):
            await bot.send_message(call.message.chat.id, info['text'][x:x + 4096])
            print(1)
        await call.answer()

    elif action == 'stop':  # Триггер нажатия на кнопку возврата в меню
        print('Стоп')
        state = dp.current_state(user=call.from_user.id)
        await state.set_state(States.all()[0])
        await bot.send_message(call.message.chat.id, 'И вот вы снова в меню', reply_markup=markup_menu)
        await call.answer()

    elif action == "behind":  # Триггер нажатия на кнопку просмотра предыдущего SCP
        print('Назад')
        info = u.browse(f'{int(num_SCP) - 1}', call.message.chat.id)
        print(info['text'])
        await bot.send_photo(call.message.chat.id, info['img'])
        for x in range(0, len(info['text']), 4096):
            await bot.send_message(call.message.chat.id, info['text'][x:x + 4096])
            print(1)
        await call.answer()


@dp.callback_query_handler(Text(startswith="change_"),
                           state=States.STATE1_WORK)  # Обработка запросов инлайн кнопок смены имени и фото
async def callbacks_num(call: types.CallbackQuery):
    action = call.data.split("_")[1]
    if action == "photo":  # Триггер нажатия на кнопку смены фото
        await bot.send_message(call.message.chat.id, "Пришлите новую фотографию:")
        state = dp.current_state(user=call.from_user.id)
        await state.set_state(States.all()[2])
        await call.answer()
    elif action == 'name':  # Триггер нажатия на кнопку смены имени
        await bot.send_message(call.message.chat.id, 'Введите новое имя профиля')
        state = dp.current_state(user=call.from_user.id)
        await state.set_state(States.all()[3])
        await call.answer()


@dp.message_handler(Text(equals="Мой профиль"),
                    state=States.STATE1_WORK | States.STATE4_PHOTO)  # Выводим профиль пользователя
async def with_puree(msg: types.Message):
    await msg.reply("Это ваш профиль, любуйтесь", reply_markup=markup_profile)
    cur = conn.cursor()
    profile = cur.execute(f'''SELECT * FROM users WHERE userid = {msg.from_user.id}''').fetchall()
    conn.commit()
    await bot.send_photo(msg.chat.id, str(profile[0][7]))
    await bot.send_message(msg.chat.id,
                           f'Имя: {profile[0][8]}.\nДата регистрации: {profile[0][6]}.\nКоличество запросов: {profile[0][4]}.\n'
                           f'Уровень {profile[0][3]}.\n \nЧтобы повысить уровень делайте больше запросов',
                           reply_markup=u.get_keyboard_change())


@dp.message_handler(Text(equals="Меню"), state=States.all())  # Выводим меню пользователю
async def with_puree(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[0])
    await message.reply("Вы в главном меню", reply_markup=markup_menu)


@dp.message_handler(Text(equals="Поиск SCP"),
                    state=States.STATE1_WORK)  # Переход в статус получения номера SCP от пользователя
async def with_puree(message: types.Message):
    await message.reply("Введите номер SCP", reply_markup=greet_search)
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[1])  # Вот тут включается статус поиска


@dp.message_handler(Text(equals="Активировать протокол поиска"),
                    state=States.STATE2_SEARCH)  # После нажатия этой кнопки должна появиться информация об SCP объекте
async def with_puree(msg: types.Message):
    cur = conn.cursor()
    num_SCP = cur.execute(f'''SELECT last_scp FROM users WHERE userid = {msg.from_user.id}''').fetchall()[0][0]
    if num_SCP:  # Проверка на то вводил ли пользователь вообще номер SCP
        info = u.browse(f'{num_SCP}', msg.chat.id)
        await bot.send_photo(msg.chat.id, info['img'])
        for x in range(0, len(info['text']), 4096):
            await bot.send_message(msg.chat.id, info['text'][x:x + 4096])
        await bot.send_message(msg.chat.id, u.phrasebook['end_search'],
                               reply_markup=u.get_keyboard_search(num_SCP))
    else:
        await msg.reply('Вы не указали номер SCP')


@dp.message_handler(state=States.STATE5_NAME)  # Прием нового имени профиля и смена его в БД
async def get_text_messages(msg: types.Message):
    await msg.reply('C этого момента я буду звать вас ' + msg.text)
    cur = conn.cursor()
    cur.execute(f"""UPDATE users SET nickname = '{msg.text}' WHERE userid = {msg.from_user.id}""")
    conn.commit()

    state = dp.current_state(user=msg.from_user.id)
    await state.set_state(States.all()[0])


@dp.message_handler(content_types=[types.ContentType.PHOTO],
                    state=States.STATE4_PHOTO)  # Прием нового Фото  профиляи смена его в БД
async def edit_photo(msg: types.Message):
    document_id = msg.photo[0].file_id
    file_info = await bot.get_file(document_id)
    cur = conn.cursor()
    cur.execute(f"""UPDATE users SET photo = '{file_info.file_id}' WHERE userid = {msg.from_user.id}""")
    conn.commit()
    await bot.send_message(msg.from_user.id, 'Фотография  успешно загружена')


@dp.message_handler(content_types=[types.ContentType.TEXT],
                    state=States.STATE4_PHOTO)  # Заглушка для текстовых сообщений в режиме смены фото
async def edit_photo(msg: types.Message):
    await msg.reply("Отправьте фото, либо вернитесь в профиль", reply_markup=return_profile)


@dp.message_handler()  # Заглушка для без статусного ввода
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'Необходимо перезапусить бота с помощью /start')


@dp.message_handler(state=States.STATE2_SEARCH)  # Заглушка для текстовых сообщений в режиме поиска SCP
async def with_puree(message: types.Message):
    cur = conn.cursor()
    if message['text'].isdigit():
        cur.execute(f'''UPDATE users SET last_scp = {message['text']} WHERE userid = {message.from_user.id}''')
        conn.commit()
        await message.reply("Верный ввод")
    else:
        await message.reply("Ошибка ввода!\n\nВведите номер SCP без лишних знаков")


@dp.message_handler(content_types=[types.ContentType.TEXT],
                    state=States.STATE1_WORK)  # Заглушка приема сообщения при 1 статусе
async def get_text_messages(msg: types.Message):
    await msg.reply(
        f'{msg.from_user.first_name}, архив не может обработать данный тип информации, используйте команды.')


async def shutdown(dispatcher: Dispatcher):  # Функция закрытия соединения с хранилищем состояний
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp)