import argparse
import time
from urllib.parse import unquote, urlsplit

import requests
from downloaded_tools import get_book_soup, parse_book_page, generate_file_full_path, download_txt, download_image

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Скачиваем книги с start_id  до end_id с сайта https://tululu.org '
    )
    parser.add_argument(
        'start_id', help='Номер книги с которого начинаем', type=int)
    parser.add_argument(
        'end_id', help='Номер на котором заканчиваем', type=int)
    args = parser.parse_args()
    book_id = args.start_id
    while book_id < args.end_id:
        try:
            try:
                soup = get_book_soup(f'https://tululu.org/b{book_id}/')
            except requests.HTTPError as error:
                print(f"Некорректный id для книги: {book_id}", error)
                book_id += 1
                continue
            book_description = parse_book_page(soup, book_id)
            title = book_description['title']
            filename_for_txt = f"{book_id}.{title}.txt"
            try:
                fullpath_for_txt = generate_file_full_path(filename_for_txt, 'books/')
                if fullpath_for_txt:
                    download_txt(book_id, fullpath_for_txt)
            except requests.HTTPError as error:
                print(f'Книги нет на сайте id: {book_id}', error)
                book_id += 1
                continue
            url_for_image = book_description['image_url']
            image_filename = unquote(
                urlsplit(url_for_image).path).split('/')[-1]
            try:
                fullpath_for_image = generate_file_full_path(image_filename, 'images/')
                if fullpath_for_image:
                    download_image(url_for_image, fullpath_for_image)
            except requests.HTTPError as error:
                print("Ошибка загрузки картинки", error)
                book_id += 1
                continue
            book_id += 1
        except requests.exceptions.ConnectionError as error:
            print('Проблемы с соединением ожидаем 4 секунды', error)
            time.sleep(4)
            continue
