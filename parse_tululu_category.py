import json
import os.path
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, unquote, urlsplit

import argparse
import requests
from bs4 import BeautifulSoup

from downloaded_tools import get_book_soup, parse_book_page, generate_file_full_path, download_txt, download_image


def get_books_ids_by_page(soup: BeautifulSoup) -> list[str]:
    selector = 'table.d_book'
    books = soup.select(selector)
    return [book.select_one('a')['href'][2:-1] for book in books]


def save_books_description(description: list, filename=Path('description.json')):
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(json.dumps(description, indent=2, ensure_ascii=False))


def get_book_descriptions(description_filename='description.json'):
    if os.path.isfile(description_filename):
        with open(description_filename, 'r', encoding='UTF-8') as f:
            return json.load(f)
    return []


def main():
    parser = argparse.ArgumentParser("Скрипт для постраничного скачивания книг фантастики")
    parser.add_argument("--start_page", type=int, default=1, help='Первая  страница для скачивания')
    parser.add_argument("--end_page", type=int, default=2, help='Последняя страница для скачивания')
    parser.add_argument("--folder", type=str, default='downloaded',
                        help='Путь к каталогу для скачиваемых материалов')
    parser.add_argument("--skip_img", action="store_true")
    parser.add_argument("--skip_txt", action="store_true")
    args = parser.parse_args()
    os.makedirs(args.folder, exist_ok=True)
    book_ids = []
    base_url = "https://tululu.org/l55/"
    for page_num in range(args.start_page, args.end_page):
        try:
            soup = get_book_soup(urljoin(base_url, str(page_num)))
            book_ids += get_books_ids_by_page(soup)
        except requests.exceptions.ConnectionError as error:
            print('Проблемы с соединением ожидаем 4 секунды', error, file=sys.stderr)
            time.sleep(4)
            continue
        except  requests.HTTPError as error:
            print('Неверный url', error, file=sys.stderr)
            continue
    book_descriptions = get_book_descriptions()
    for book_id in book_ids:
        try:
            try:
                soup = get_book_soup(f'https://tululu.org/b{book_id}/')
            except requests.HTTPError as error:
                print(f"Некорректный id для книги: {book_id}", error)
                continue
            book_description = parse_book_page(soup, book_id)
            if not args.skip_txt:
                title = book_description['title']
                filename_for_txt = f"{book_id}.{title}.txt"
                try:
                    fullpath_for_txt = generate_file_full_path(filename_for_txt, str(Path(args.folder, 'books/')))
                    book_description['book_path'] = fullpath_for_txt
                    if fullpath_for_txt:
                        download_txt(book_id, fullpath_for_txt)
                except requests.HTTPError as error:
                    print(f'Книги нет на сайте id: {book_id}', error)
                    continue
            else:
                book_description['book_path'] = None
            if not args.skip_img:
                url_for_image = book_description['image_url']
                image_filename = unquote(
                    urlsplit(url_for_image).path).split('/')[-1]
                try:
                    fullpath_for_image = generate_file_full_path(image_filename, str(Path(args.folder, 'images/')))
                    if fullpath_for_image:
                        download_image(url_for_image, fullpath_for_image)
                    book_description['image_path'] = fullpath_for_image or str(Path(args.folder, 'images', 'nopic.gif'))
                except requests.HTTPError as error:
                    print("Ошибка загрузки картинки", error)
                    continue
            else:
                book_description['image_path'] = None
            book_descriptions.append(book_description)
        except requests.exceptions.ConnectionError as error:
            print('Проблемы с соединением ожидаем 4 секунды', error)
            time.sleep(4)
            continue
    save_books_description(book_descriptions, Path(args.folder, 'description.json'))


if __name__ == "__main__":
    main()
