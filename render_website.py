import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
def rebuild():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    with open("downloaded/description.json", 'r') as f:
        books_description = json.load(f)

    rendered_page = template.render({'books': books_description})
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print('rebuilded')

rebuild()
server = Server()
server.watch('template.html',rebuild)
server.serve(root='.')