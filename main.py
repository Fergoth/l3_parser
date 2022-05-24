import requests
import os

if not os.path.exists('books'):
    os.makedirs('books')
url = "https://tululu.org/txt.php?id={}"
for id in range(1,11):
    response = requests.get(url.format(id))
    response.raise_for_status()
    filename = 'books/book_{id}.txt'.format(id=id)
    if os.path.exists(filename): continue
    with open(filename, 'wb') as file:
        file.write(response.content)
