import requests
import os

def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()

if not os.path.exists('books'):
    os.makedirs('books')
url = "https://tululu.org/txt.php?id={}"
for id in range(1,11):
    response = requests.get(url.format(id))
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError as error:
        print(error)
        continue
    filename = 'books/book_{id}.txt'.format(id=id)
    if os.path.exists(filename): continue
    with open(filename, 'wb') as file:
        file.write(response.content)
