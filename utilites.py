from bs4 import BeautifulSoup
import requests


def get_content(url, id='page-content'):
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    items = soup.find('div', id=id).text.strip()
    return str(items)



