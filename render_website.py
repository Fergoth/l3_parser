import argparse
import json
import os
from os import PathLike
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def rebuild(settings_path):
    books_per_page = 20
    books_per_column = 2
    html_folder = 'pages'
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    os.makedirs(html_folder,exist_ok=True)

    template = env.get_template('template.html')
    try:
        with open(Path(settings_path), 'r') as f:
            books_description = json.load(f)
    except FileNotFoundError:
        print("Некорректный путь до настроек, перезапустите скрипт.")
        exit(0)
    for book in books_description:
        book['book_path'] = os.path.join('..',quote(book['book_path']))
        book['image_path'] = os.path.join('..', quote(book['image_path']))
    pages = list(chunked(books_description,n=books_per_page))
    for page_num, page in enumerate(pages, start=1):
        current_page = page_num
        rendered_page = template.render(
            {
                'books': chunked(page, books_per_column),
                'pages_count': len(pages),
                'current_page': current_page
            }
        )
        filepath = os.path.join(html_folder,f'index{current_page}.html')
        with open(filepath, 'w', encoding='utf8') as file:
            file.write(rendered_page)

if __name__=='__main__':
    parser = argparse.ArgumentParser("Скрипт для запуска локального сайта со скаченными книгами")
    parser.add_argument("--path_to_settings", type=str, default='media/description.json',help='Путь к файлу настроек')
    args = parser.parse_args()
    rebuild(args.path_to_settings)
    server = Server()
    server.watch('template.html',rebuild)
    server.serve(root='.')