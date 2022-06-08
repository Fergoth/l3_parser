import requests
import os
from pathvalidate import sanitize_filename

def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()




def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError as error:
        print(error)
    if not os.path.exists(folder):
        os.makedirs(folder)
    name = sanitize_filename(filename) + '.txt'
    fullpath = os.path.join(folder,name)
    #if os.path.exists(fullpath): continue
    with open(fullpath, 'wb') as file:
        file.write(response.content)
    return fullpath
# if not os.path.exists('books'):
#     os.makedirs('books')
# url = "https://tululu.org/txt.php?id={}"
# for id in range(1,11):
#     response = requests.get(url.format(id))
#     response.raise_for_status()
#     try:
#         check_for_redirect(response)
#     except requests.HTTPError as error:
#         print(error)
#         continue
#     filename = 'books/book_{id}.txt'.format(id=id)
#     if os.path.exists(filename): continue
#     with open(filename, 'wb') as file:
#         file.write(response.content)

url = 'http://tululu.org/txt.php?id=1'

filepath = download_txt(url, 'Алиби')
print(filepath)  # Выведется books/Алиби.txt

filepath = download_txt(url, 'Али/би', folder='books/')
print(filepath)  # Выведется books/Алиби.txt

filepath = download_txt(url, 'Али\\би', folder='txt/')
print(filepath)  # Выведется txt/Алиби.txt
