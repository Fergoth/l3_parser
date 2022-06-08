import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup

def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()

def get_title(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    h1 = soup.find('h1').text
    print(h1)
    title, author = map(lambda x : x.strip(), h1.split('::'))
    return title

def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    if not os.path.exists(folder):
        os.makedirs(folder)
    name = sanitize_filename(filename) + '.txt'
    fullpath = os.path.join(folder, name)
    os.path.exists(fullpath):
        return fullpath
    with open(fullpath, 'wb') as file:
        file.write(response.content)
    return fullpath


if __name__ == "__main__":
    for id in range(1, 11):
        url_for_title = 'https://tululu.org/b{}/'.format(id)
        url_for_txt = "https://tululu.org/txt.php?id={}".format(id)
        try:
            title = get_title(url_for_title)
            fname  = f"{id}.{title}"
            download_txt(url_for_txt,fname)
        except requests.HTTPError as error:
            print(error)
            continue
