import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()

def get_book_soup(url:str)->BeautifulSoup:
    """Функция для получения информации со страницы с книгой
    Args:
        url: url книги на сайте tululu
    Returns:
        soup(BeautifulSoup) : объект BeautifulSoup соответствующий странице с книгой
    """
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, 'lxml')

def get_title(book_soup):
    h1 = book_soup.select_one('h1').text
    title, _ = map(lambda x: x.strip(), h1.split('::'))
    return title


def get_author(book_soup):
    h1 = book_soup.select_one('h1').text
    _, author = map(lambda x: x.strip(), h1.split('::'))
    return author


def get_url_image(soup, book_id):
    image_url = soup.select_one('div.bookimage img')['src']
    image_full_url = urljoin(
        'https://tululu.org/b{}/'.format(book_id), image_url)
    return image_full_url


def get_comments(soup):
    raw_comments = soup.select('div.texts')
    comments = [raw_comment.select_one('span').text for raw_comment in raw_comments]
    return comments


def get_genres(soup):
    raw_genres = soup.select('span.d_book a')
    genres = [raw_genre.text for raw_genre in raw_genres]
    return genres


def parse_book_page(soup, book_id):
    return {
        'genres': get_genres(soup),
        'comments': get_comments(soup),
        'image_url': get_url_image(soup, book_id),
        'title': get_title(soup),
        'author': get_author(soup)
    }

def download_image(url, fullpath):
    """Функция для скачивания картинок.
    Args:
        url (str): Ссылка на картинку, которую хочется скачать.
        fullpath (str): Полный куда сохраняем файл.
    Returns:
        str: Путь до файла, куда сохранена картинка.
    """

    response = requests.get(url)
    response.raise_for_status()
    with open(fullpath, 'wb') as file:
        file.write(response.content)
    return fullpath


def download_txt(book_id, fullpath):
    """Функция для скачивания текстовых файлов.
    Args:
        book_id (str): Айди книги, которую хочется скачать.
        fullpath (str): Полный куда сохраняем файл.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    url = "https://tululu.org/txt.php"
    payload = {'id': book_id}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    with open(fullpath, 'wb') as file:
        file.write(response.content)
    return fullpath


def file_full_path(filename, folder):
    os.makedirs(folder, exist_ok=True)
    name = f"{sanitize_filename(filename)}"
    fullpath = os.path.join(folder, name)
    if os.path.exists(fullpath):
        return None
    return fullpath