import requests
import os
from urllib.parse import unquote, urlsplit, urljoin
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def get_title(soup):
    h1 = soup.find('h1').text
    title, _ = map(lambda x: x.strip(), h1.split('::'))
    return title


def get_author(soup):
    h1 = soup.find('h1').text
    _, author = map(lambda x: x.strip(), h1.split('::'))
    return author


def get_url_image(soup):
    image_url = soup.find('div', class_='bookimage').find('img')['src']
    image_full_url = urljoin("https://tululu.org/", image_url)
    return image_full_url


def get_comments(soup):
    raw_comments = soup.find_all('div', class_='texts')
    comments = [i.find('span').text for i in raw_comments]
    return comments


def parse_book_page(id):
    """Функция для получения информации со страницы с книгой
    Args:
        id(int) : id номер книги на сайте tululu
    Returns:
        soup(BeautifulSoup) : объект BeautifulSoup соответствующий странице с книгой
    """
    url = 'https://tululu.org/b{}/'.format(id)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def download_image(url, filename=None, folder='images'):
    """Функция для скачивания картинок.
    Args:
        url (str): Cсылка на картинку, которую хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранена картинка.
    """
    response = requests.get(url)
    response.raise_for_status()
    # print(unquote(urlsplit(image_full_url).path))
    file_ext = unquote(urlsplit(url).path).split('/')[-1]
    if not filename:
        filename = unquote(urlsplit(url).path).split('/')[-1]
    print("имя файла : ", filename)
    print(f"Ссылка на картинку: {url}")
    if not os.path.exists(folder):
        os.makedirs(folder)
    name = f"{sanitize_filename(filename)}"
    fullpath = os.path.join(folder, name)
    if os.path.exists(fullpath):
        print("Уже скачано")
        return fullpath
    with open(fullpath, 'wb') as file:
        file.write(response.content)
    return fullpath


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
    check_for_redirect(response)
    if not os.path.exists(folder):
        os.makedirs(folder)
    name = sanitize_filename(filename) + '.txt'
    fullpath = os.path.join(folder, name)
    if os.path.exists(fullpath):
        print("Уже скачано")
        return fullpath
    with open(fullpath, 'wb') as file:
        file.write(response.content)
    return fullpath


if __name__ == "__main__":
    for id in range(1, 11):
        url_for_txt = "https://tululu.org/txt.php?id={}".format(id)
        try:
            soup = parse_book_page(id)

        except requests.HTTPError as error:
            #print("Ошибка при парсинге страницы",error)
            continue
        title = get_title(soup)
        comments = get_comments(soup)
        print(title,end = '\n\n')
        for comment in comments:
            print(comment)
    #         title = get_title(url_for_title)
    #         fname  = f"{id}.{title}"
    #         download_txt(url_for_txt,fname)
    #     except requests.HTTPError as error:
    #         print(error)
    #         continue
