import json

import requests
import logging
from bs4 import BeautifulSoup
from parser import headers

book_urls = []
books = []
series = []


# Parse top 100 books
def get_urls():
    url = 'https://readrate.com/rus/ratings/top100?iid=8107&offset=all'
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        books_items = soup.find_all('div', class_='col-12 col-sm ml-sm-5')
        for bi in books_items:
            book_url = bi.find('a', class_='title-link d-inline-block').get('href')
            book_urls.append(f'https://readrate.com/{book_url}')
        get_top_books()
    else:
        logging.error(f'Status Code: {response.status_code}')


# Get top 100 books
def get_top_books():
    for book_url in book_urls:
        query = requests.get(url=book_url, headers=headers)
        if query.status_code == 200:
            result = query.content
            soup = BeautifulSoup(result, 'html.parser')
            title = soup.find('h1', class_='book-title').get_text()
            author = soup.find('li', class_='contributor item text-wrap list-inline-item').get_text()
            images = soup.find_all('img', src=True)
            img = "{}{}".format('https://readrate.com/', images[3].get('data-src'))
            try:
                genre = soup.find('a', class_='link d-block font-size-sm').get_text()
                buy_link = soup.find('a', class_='btn btn-pb btn-primary px-4').get('href')
                buy_link2 = soup.find('div', id='paper').find('a').get('href')
            except AttributeError:
                if genre is None:
                    genre = 'Bible'
                buy_link2 = 'https://www.litres.ru'
            # refactor
            dsc = soup.find('div', class_='more-less').find_all('div', class_='entity').pop().get_text().strip()
            # refactor
            stars = soup.find('ul', class_='stars-list list-unstyled list-inline align-middle d-inline-block') \
                .find_all('li', class_='list-inline-item star active')
            index = book_urls.index(book_url)
            book_to_json(index, author, title, genre, dsc, len(stars), img, buy_link, buy_link2)
        else:
            logging.warning(f'Status Code: {query.status_code}')
            continue
    with open('json/top_books.json', 'w') as f:
        json.dump(books, f, indent=2)


def book_to_json(book_id, author, title, genre, dsc, stars, img, buy_link, buy_link2):
    to_json = {'id': book_id, 'title': title, 'author': author, 'genre': genre, 'description': dsc, 'stars': stars,
               'image': img, 'buy_link_1': buy_link, 'buy_link_2': buy_link2}
    books.append(to_json)
    print(f'Book {title} saved.')


# Parse all series to Json
def get_series_urls():
    for i in range(1, 8):
        url = f'https://readrate.com/rus/series?page={i}'
        query = requests.get(url=url, headers=headers)
        if query.status_code == 200:
            result = query.content
            soup = BeautifulSoup(result, 'html.parser')
            links = soup.find_all('a', class_='title-link align-middle d-inline-block')
            for j in range(0, len(links)):
                name = links[j].get_text()
                link = f"https://readrate.com/rus/series/popular?page={i}"
                index = j
                series_to_json(name, link, index)
            with open('json/all_series.json', 'w') as f:
                json.dump(series, f, indent=2)
        else:
            logging.error(f'Status Code: {query.status_code}')
            continue


def series_to_json(name, link, index):
    to_json = {'name': name, 'link': link, 'index': index}
    series.append(to_json)
    print(f'Series {name} saved.')


if __name__ == '__main__':
    get_urls()
    get_series_urls()
