from bs4 import BeautifulSoup
import requests


# Файл с функциями для упрощения чтения кода

def get_content(url, id='page-content'):  # Функция чтения нужной информации со страницы обьекта scp
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    items = soup.find('div', id=id).text.strip()
    return str(items)
