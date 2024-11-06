import json
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def rebuild():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    with open("downloaded/description.json", 'r') as f:
        books_description = json.load(f)
    for book in books_description:
        book['book_path'] = quote(book['book_path'])

    rendered_page = template.render({'books': chunked(books_description,2)})
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print('rebuilded')

if __name__=='__main__':
    rebuild()
    server = Server()
    server.watch('template.html',rebuild)
    server.serve(root='.')