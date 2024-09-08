import json
import time
from urllib.parse import urljoin, unquote, urlsplit

import argparse
import requests
from bs4 import BeautifulSoup

from main import get_book_soup, parse_book_page, file_full_path, download_txt, download_image


def get_fantastic_books_soup(page: int) -> BeautifulSoup:
    base_url = "https://tululu.org/l55/"
    url = urljoin(base_url, str(page))
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'lxml')


def get_books_ids_by_page(page_num : int, base_url: str)-> list[str]:
    soup = get_fantastic_books_soup(page_num)
    selector = 'table.d_book'
    books_info = soup.select(selector)
    return [book.select_one('a')['href'][2:-1] for book in books_info]

def save_books_description(description: list,filename = 'description.json'):
    with open(filename,'w',encoding='UTF-8') as f:
        f.write(json.dumps(description,indent=2, ensure_ascii=False))

def main(pages:int):
    base_url = 'https://tululu.org'
    book_ids = []
    for page_num in range(1,pages+1):
        book_ids+=get_books_ids_by_page(page_num,base_url)
    books_description = []
    for book_id in book_ids:
        try:
            try:
                soup = get_book_soup(book_id)
            except requests.HTTPError as error:
                print(f"Некорректный id для книги: {book_id}", error)
                continue
            book_description = parse_book_page(soup, book_id)
            title = book_description['title']
            filename_for_txt = f"{book_id}.{title}.txt"
            try:
                fullpath_for_txt = file_full_path(filename_for_txt, 'books/')
                book_description['book_path'] = fullpath_for_txt
                if fullpath_for_txt:
                    download_txt(book_id, fullpath_for_txt)
            except requests.HTTPError as error:
                print(f'Книги нет на сайте id: {book_id}', error)
                continue
            url_for_image = book_description['image_url']
            image_filename = unquote(
                urlsplit(url_for_image).path).split('/')[-1]
            try:
                fullpath_for_image = file_full_path(image_filename, 'images/')
                if fullpath_for_image:
                    download_image(url_for_image, fullpath_for_image)
                book_description['image_path'] = fullpath_for_image
            except requests.HTTPError as error:
                print("Ошибка загрузки картинки", error)
                continue
            books_description.append(book_description)
        except requests.exceptions.ConnectionError as error:
            print('Проблемы с соединением ожидаем 4 секунды', error)
            time.sleep(4)
            continue
    save_books_description(books_description)
if __name__ == "__main__":
    parser = argparse.ArgumentParser("Скрипт для постраничного скачивания книг фантастики")
    parser.add_argument("--pages", type=int,default=1,help='Количество страниц для скачивания')
    args = parser.parse_args()
    main(args.pages)

