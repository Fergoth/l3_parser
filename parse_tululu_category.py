from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def get_fantastic_books_soup(page: int) -> BeautifulSoup:
    base_url = "https://tululu.org/l55/"
    url = urljoin(base_url, str(page))
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'lxml')


if __name__ == "__main__":
    base_url = 'https://tululu.org'
    soup = get_fantastic_books_soup()
    books_info = soup.find_all('table', class_='d_book')
    books_ids = [book.find('a')['href'] for book in books_info]
    book_urls = [urljoin(base_url, id) for id in books_ids]
    print(book_urls)
