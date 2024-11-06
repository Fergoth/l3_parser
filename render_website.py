import json
import os
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def rebuild():
    books_per_page = 20
    html_folder = 'pages'
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    os.makedirs(html_folder,exist_ok=True)

    template = env.get_template('template.html')
    with open("downloaded/description.json", 'r') as f:
        books_description = json.load(f)

    for book in books_description:
        book['book_path'] = quote(book['book_path'])

    for page_num, page in enumerate(chunked(books_description,n=books_per_page)):
        rendered_page = template.render({'books': chunked(page,2)})
        filepath = os.path.join(html_folder,f'index{page_num+1}.html')
        with open(filepath, 'w', encoding="utf8") as file:
            file.write(rendered_page)
    print('rebuilded')

if __name__=='__main__':
    rebuild()
    server = Server()
    server.watch('template.html',rebuild)
    server.serve(root='.')