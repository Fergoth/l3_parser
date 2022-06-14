import argparse
import os
from urllib.parse import unquote, urlsplit, urljoin

from bs4 import BeautifulSoup
import requests
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def get_title(soup):
    h1 = soup.find('h1').text
    title, _ = map(lambda x: x.strip(), h1.split('::'))
    return title


def get_author(soup):
    h1 = soup.find('h1').text
    _, author = map(lambda x: x.strip(), h1.split('::'))
    return author


def get_url_image(soup, book_id):
    image_url = soup.find('div', class_='bookimage').find('img')['src']
    image_full_url = urljoin('https://tululu.org/b{}/'.format(book_id), image_url)
    return image_full_url


def get_comments(soup):
    raw_comments = soup.find_all('div', class_='texts')
    comments = [i.find('span').text for i in raw_comments]
    return comments


def get_genres(soup):
    raw_genres = soup.find('span', class_='d_book').find_all('a')
    genres = [i.text for i in raw_genres]
    return genres


def parse_book_page(soup, book_id):
    return {
        'genres': get_genres(soup),
        'comments': get_comments(soup),
        'image_url': get_url_image(soup, book_id),
        'title': get_title(soup),
        'author': get_author(soup)
    }


def get_book_soup(id):
    """Функция для получения информации со страницы с книгой
    Args:
        id(int) : id номер книги на сайте tululu
    Returns:
        soup(BeautifulSoup) : объект BeautifulSoup соответствующий странице с книгой
    """
    url = 'https://tululu.org/b{}/'.format(id)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def download_image(url, filename, folder='images/'):
    """Функция для скачивания картинок.
    Args:
        url (str): Cсылка на картинку, которую хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранена картинка.
    """
    os.makedirs(folder, exist_ok=True)
    name = f"{sanitize_filename(filename)}"
    response = requests.get(url)
    response.raise_for_status()
    name = f"{sanitize_filename(filename)}"
    fullpath = os.path.join(folder, name)
    with open(fullpath, 'wb') as file:
        file.write(response.content)
    return fullpath


def download_txt(book_id, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    url = "https://tululu.org/txt.php"
    payload = {'id' : book_id}
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    name = f"{sanitize_filename(filename)}.txt"
    fullpath = os.path.join(folder, name)
    with open(fullpath, 'wb') as file:
        file.write(response.content)
    return fullpath

def book_txt_exist(filename, folder='books/'):
    name = f"{sanitize_filename(filename)}.txt"
    fullpath = os.path.join(folder, name)
    return os.path.exists(fullpath)

def image_exist(filename, folder='images/'):
    name = f"{sanitize_filename(filename)}"
    fullpath = os.path.join(folder, name)
    return os.path.exists(fullpath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Скачиваем книги с start_id  до end_id с сайта https://tululu.org '
    )
    parser.add_argument(
        'start_id', help='Номер книги с которого начинаем', type=int)
    parser.add_argument(
        'end_id', help='Номер на котором заканчиваем', type=int)
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id):
        print('\n')
        try:
            soup = get_book_soup(book_id)
        except requests.HTTPError as error:
            print("Некорректный id для книги" ,error)
            continue
        book_description = parse_book_page(soup,book_id)
        print(book_description['title'])
        print(book_description['genres'])
        title = book_description['title']
        filename_for_txt = f"{book_id}.{title}"
        try:
            if not book_txt_exist(filename_for_txt):
                download_txt(book_id, filename_for_txt)
        except requests.HTTPError as error:
            print('Книги нет на сайте',error)
            continue
        url_for_image = book_description['image_url']
        image_filename = unquote(urlsplit(url_for_image).path).split('/')[-1]
        try:
            if not image_exist(image_filename):
                download_image(url_for_image,image_filename)
        except requests.HTTPError as error:
            print("Ошибка загрузки картинки",error)
            continue
