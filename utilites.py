from aiogram import types
from bs4 import BeautifulSoup
import requests


# Файл с функциями для упрощения чтения кода

phrasebook = {
    "end_search":f"{'—'* 15}\nПродолжите просмотр данных? Ручной ввод активирован"

}

def get_content(url, id='page-content'):  # Функция чтения нужной информации со страницы обьекта scp
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    items = soup.find('div', id=id).text.strip()
    return str(items)

def get_keyboard(num):
    # Генерация клавиатуры.
    _scp = str(int(num) - 1)
    scp_ = str(int(num) + 1)
    if len(_scp) < 3 or len(scp_) < 3:
        _scp = '0' * (3 - len(_scp)) + _scp
        scp_ = '0' * (3 - len(scp_)) + scp_
    buttons = [
        types.InlineKeyboardButton(text="SCP-" + _scp, callback_data="btn_behind"),
        types.InlineKeyboardButton(text="Остановить протокол", callback_data="btn_stop"),
        types.InlineKeyboardButton(text="SCP-" + scp_, callback_data="btn_front")]

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    return keyboard

