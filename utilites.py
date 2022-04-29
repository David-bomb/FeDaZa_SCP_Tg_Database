from aiogram import types
import main as m
from bs4 import BeautifulSoup
import requests
import logging
from language import languages

# Файл с функциями для упрощения чтения кода

phrasebook = {
    "end_search": f"Продолжите просмотр данных? Ручной ввод активирован"

}
logging.basicConfig(
    filename='errors.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.ERROR
)
profile = ''


def get_content(url, id='page-content'):  # Функция чтения нужной информации со страницы обьекта scp
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    items = soup.find('div', id=id).text.strip()
    return str(items)


def get_keyboard_search(num):
    # Генерация клавиатуры.
    _scp = str(int(num) - 1)
    scp_ = str(int(num) + 1)
    if len(_scp) < 3 or len(scp_) < 3:
        _scp = '0' * (3 - len(_scp)) + _scp
        scp_ = '0' * (3 - len(scp_)) + scp_
    buttons = [
        types.InlineKeyboardButton(text="SCP-" + _scp, callback_data="search_behind"),
        types.InlineKeyboardButton(text="Остановить протокол", callback_data="search_stop"),
        types.InlineKeyboardButton(text="SCP-" + scp_, callback_data="search_front")]

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    return keyboard


def get_keyboard_change():
    # Генерация клавиатуры.
    buttons = [
        types.InlineKeyboardButton(text="Сменить фото профиля", callback_data="change_photo"),
        types.InlineKeyboardButton(text="Сменить имя профиля", callback_data="change_name")]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def browse(argument, id):
    retur = {'img': None, 'text': None}
    cur = m.conn.cursor()
    print('Ищу ошибку 1 - курсор-словарь')
    language = cur.execute(f'''SELECT language FROM users WHERE userid = {id}''').fetchall()[0][0]
    cur.execute(f'''UPDATE users SET last_scp = {argument} WHERE userid = {id}''')
    print('Ищу ошибку 2 - запрос')
    if len(argument) < 3:
        argument = '0' * (3 - len(argument)) + argument
    if argument:  # проверяем, ввели ли аргумент
        print('Ищу ошибку 3 нарезка-аргумент')
        try:  # Пытаемся найти этот объект, в противном случае пишем что не нашли
            print('Ищу ошибку 4 try')
            browse = {
                'RU': f'http://scp-ru.wikidot.com/scp-{argument}',
                'EN': f'https://scp-wiki.wikidot.com/scp-{argument}'
            }
            print('debug')
            info = get_content(browse[language], id='page-title') + '\n' + \
                   get_content(browse[language])  # Создаём ответ бота
            text = requests.get(browse[language]).text
            print('Ищу ошибку 6 - создание инфы')
            try:
                if language == 'RU':
                    retur['img'] = BeautifulSoup(text, 'html.parser').find(class_="rimg").find(
                        class_="image").get(
                        'src')
                elif language == 'EN':
                    retur['img'] = BeautifulSoup(text, 'html.parser').find(
                        class_="scp-image-block block-right").find(class_="image").get('src')
            except:
                print('Ищу Ошибку 5 - except')
                retur['img'] = 'AgACAgIAAxkBAAIDd2JcUPUnu4OrqO59i9-M4FSRz3CmAALauDEbwQLoSo_J1EadLNMAAQEAAwIAA3MAAyQE'
            retur['text'] = info
            return retur
        except Exception as e:  # Запись ошибки в лог, если пользователь столкнулся с ошибкой разряда ERROR или FATAL, возможно появление логов от самого aiogram
            logging.error(str(e))
            cur = m.conn.cursor()
            cur.execute(  # Фиксирование ошибки и прикрепление ошибки к пользователю, для возможного опроса в будущем
                f'''UPDATE users SET number_of_bugs = number_of_bugs + 1 WHERE userid = {id})''')
            m.conn.commit()
            retur['text'] = languages['language_error'][language]
            return retur
    else:
        retur['text'] = languages['language_error'][language]
        return retur
