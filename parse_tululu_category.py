import json
import os.path
import time
from pathlib import Path
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

def save_books_description(description: list,filename = Path('description.json')):
    with open(filename,'w',encoding='UTF-8') as f:
        f.write(json.dumps(description,indent=2, ensure_ascii=False))


def get_book_description(description_filename = 'description.json'):
    if os.path.isfile(description_filename):
        with open(description_filename,'r',encoding='UTF-8') as f:
            return json.load(f)
    return []


def main(start_page:int, end_page:int,folder:str,skip_txt:bool,skip_img:bool):
    base_url = 'https://tululu.org'
    book_ids = []
    for page_num in range(start_page,end_page):
        book_ids+=get_books_ids_by_page(page_num,base_url)
    books_description = get_book_description()
    for book_id in book_ids:
        try:
            try:
                soup = get_book_soup(book_id)
            except requests.HTTPError as error:
                print(f"Некорректный id для книги: {book_id}", error)
                continue
            book_description = parse_book_page(soup, book_id)
            if not skip_txt:
                title = book_description['title']
                filename_for_txt = f"{book_id}.{title}.txt"
                try:
                    fullpath_for_txt = file_full_path(filename_for_txt, str(Path(folder,'books/')))
                    book_description['book_path'] = fullpath_for_txt
                    if fullpath_for_txt:
                        download_txt(book_id, fullpath_for_txt)
                except requests.HTTPError as error:
                    print(f'Книги нет на сайте id: {book_id}', error)
                    continue
            else:
                book_description['book_path'] = None
            if not skip_img:
                url_for_image = book_description['image_url']
                image_filename = unquote(
                    urlsplit(url_for_image).path).split('/')[-1]
                try:
                    fullpath_for_image = file_full_path(image_filename, str(Path(folder,'images/')))
                    if fullpath_for_image:
                        download_image(url_for_image, fullpath_for_image)
                    book_description['image_path'] = fullpath_for_image or str(Path(folder,'images','nopic.gif'))
                except requests.HTTPError as error:
                    print("Ошибка загрузки картинки", error)
                    continue
            else:
                book_description['image_path'] = None
            books_description.append(book_description)
        except requests.exceptions.ConnectionError as error:
            print('Проблемы с соединением ожидаем 4 секунды', error)
            time.sleep(4)
            continue
    save_books_description(books_description, Path(folder,'description.json'))
if __name__ == "__main__":
    parser = argparse.ArgumentParser("Скрипт для постраничного скачивания книг фантастики")
    parser.add_argument("--start_page", type=int,default=10,help='Первая  страница для скачивания')
    parser.add_argument("--end_page", type=int, default=11, help='Последняя страница для скачивания')
    parser.add_argument("--dest_folder", type=str, default='downloaded', help='Путь к каталогу для скачиваемых материалов')
    parser.add_argument("--skip_imgs", action="store_true")
    parser.add_argument("--skip_txt", action="store_true")
    args = parser.parse_args()
    main(args.start_page, args.end_page,args.dest_folder,args.skip_txt,args.skip_imgs)

