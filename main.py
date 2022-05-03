import logging
import random
import json

import requests
from bs4 import BeautifulSoup
from create_bot import BotDB

book_urls = []
books = []

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
}


# Utils
def get_random_book_from_file():
    random_book = random.randint(0, 98)
    with open('top_books.json') as f:
        data = json.loads(f.read())
    book_id = data[random_book]['id']
    title = data[random_book]['title']
    author = data[random_book]['author']
    genre = data[random_book]['genre']
    stars = data[random_book]['stars']
    image = data[random_book]['image']
    buy_link = data[random_book]['buy_link_1']
    buy_link2 = data[random_book]['buy_link_2']
    logging.info(f'Random Book Title: {title}')
    return [book_id, title, author, genre, stars, image, buy_link, buy_link2]


def get_dsc(count):
    with open('top_books.json') as f:
        data = json.loads(f.read())
    description = data[count]['description']
    return description


def book_to_json(book_id, author, title, genre, dsc, stars, img, buy_link, buy_link2):
    to_json = {'id': book_id, 'title': title, 'author': author, 'genre': genre, 'description': dsc, 'stars': stars,
               'image': img, 'buy_link_1': buy_link, 'buy_link_2': buy_link2}
    books.append(to_json)
    print(f'Book {title} saved.')


# Parser
def get_urls():
    url = 'https://readrate.com/rus/ratings/top100?iid=8107&offset=all'
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        books_items = soup.find_all('div', class_='col-12 col-sm ml-sm-5')
        for bi in books_items:
            book_url = bi.find('a', class_='title-link d-inline-block').get('href')
            book_urls.append(f'https://readrate.com/{book_url}')
        get_top_books()
    else:
        logging.error(f'Status Code: {response.status_code}')


def get_book_fl(title):
    url = f'https://flibusta.site/booksearch?ask={title}'
    query = requests.get(url)
    if query.status_code == 200:
        result = query.content
        soup = BeautifulSoup(result, 'html.parser')
        empty = soup.find('p').get_text()
        if empty == 'Ничего не найдено. Введите фамилию автора или название книги для поиска':
            return 'Error'
        books_list = soup.find_all('li')
        for book in books_list:
            try:
                link = book.find('a').get('href')
                if link.__contains__('/b/'):
                    break
            except:
                link = '#'
        if link == '#':
            return 'Error'
        download_link = f'https://flibusta.site/{link}/fb2'
        query = requests.get(download_link)
        file_path = 'user_book/book.fb2'
        with open(file_path, 'wb') as f:
            f.write(query.content)
        return file_path
    else:
        logging.warning(f'Status Code: {query.status_code}')
        return 'Error'


def get_top_books():
    for book_url in book_urls:
        query = requests.get(book_url)
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
    with open('top_books.json', 'w') as f:
        json.dump(books, f, indent=2)


def book_search(title, message_id, chat_id):
    url = f'https://readrate.com/rus/search/books?q={title}'
    query = requests.get(url)
    BotDB.add_util_data(message_id)
    book_authors_temp = ''
    book_titles_temp = ''
    book_links_temp = ''
    util_id = BotDB.get_util_id(message_id)
    if query.status_code == 200:
        result = query.content
        soup = BeautifulSoup(result, 'html.parser')
        try:
            count = int(soup.find('span', class_='current py-2 px-3 rounded d-inline-block').find('span').get_text())
            logging.info(f'Number of books: {count}')
        except:
            return False
        if count % 10 == 0:
            p = 0
        else:
            p = int(count % 10 - 1)
        q = int(count / 10)
        if p != 0:
            q += 1
        for i in range(0, q):
            url = f'https://readrate.com/rus/search/books?q={title}&offset={i * 10}'
            query = requests.get(url)
            if query.status_code != 200:
                break
            result = query.content
            soup = BeautifulSoup(result, 'html.parser')
            div = soup.find_all('div', class_='col-12 col-sm ml-sm-5')
            for j in range(0, 10):
                if (i == q - 1) and (j == p):
                    break
                tmp = div[j].find('a', class_='title-link d-inline-block')
                book_links_temp = f'https://readrate.com/{tmp.get("href")}'
                book_titles_temp = tmp.get_text()
                try:
                    tmp = div[j].find('a', class_='text-dark link').get_text()
                    book_authors_temp = tmp
                except AttributeError:
                    book_authors_temp = 'None'
                BotDB.add_book_data(message_id, chat_id, util_id, book_titles_temp, book_authors_temp, book_links_temp)
        return True


def make_message_book(empty_array, message_id, chat_id, config):
    if config:
        try:
            page_number = BotDB.get_page_number(message_id)
        except TypeError:
            page_number = 0
            BotDB.add_util_data(message_id)
            util_id = BotDB.get_util_id(message_id)
            BotDB.update_wishlist_util_id(util_id, chat_id)
        book_titles = BotDB.get_wish_title(chat_id)
        book_authors = BotDB.get_wish_author(chat_id)
    else:
        util_id = BotDB.get_util_id(message_id)
        page_number = BotDB.get_page_number(message_id)
        book_titles = BotDB.get_book_title_data(util_id, chat_id)
        book_authors = BotDB.get_book_author_data(util_id, chat_id)
    result = ''
    if len(book_titles) // 10 - page_number == 0:
        tm = len(book_titles) % 10
    else:
        tm = 10
    empty_array.append(tm)
    for i in range(0, tm):
        result += f'{i + 1}. {book_titles[i + page_number * 10][0]} - {book_authors[i + page_number * 10][0]}\n'
    return result


def get_one_book(url_book, message_id, chat_id, config):
    book_to_string = []
    if config:
        util_id = BotDB.get_util_id(message_id)
        book_links = BotDB.get_wish_link(chat_id)
        book_id = BotDB.get_wish_book_id(util_id, chat_id)
    else:
        util_id = BotDB.get_util_id(message_id)
        book_links = BotDB.get_book_link_data(util_id, chat_id)
        book_ids = BotDB.get_book_id(util_id, chat_id)
        book_id = book_ids[url_book][0]
    book_url = book_links[url_book][0]
    query = requests.get(book_url)
    if query.status_code == 200:
        result = query.content
        soup = BeautifulSoup(result, 'html.parser')
        title = soup.find('h1', class_='book-title').get_text()
        try:
            author = soup.find('li', class_='contributor item text-wrap list-inline-item').get_text()
        except AttributeError:
            author = 'None'
        images = soup.find_all('img', src=True)
        img = "{}{}".format('https://readrate.com/', images[3].get('data-src'))
        try:
            genre = soup.find('a', class_='link d-block font-size-sm').get_text()
        except AttributeError:
            genre = 'None'
        try:
            buy_link = soup.find('a', class_='btn btn-pb btn-primary px-4').get('href')
        except AttributeError:
            buy_link = 'https://www.litres.ru'
        try:
            buy_link2 = soup.find('div', id='paper').find('a').get('href')
        except AttributeError:
            buy_link2 = 'https://www.litres.ru'
        # refactor
        dsc = soup.find('div', class_='more-less').find_all('div', class_='entity').pop().get_text().strip()
        # refactor
        stars = soup.find('ul', class_='stars-list list-unstyled list-inline align-middle d-inline-block') \
            .find_all('li', class_='list-inline-item star active')
        book_to_string.append(title)
        book_to_string.append(author)
        book_to_string.append(genre)
        book_to_string.append(len(stars))
        book_to_string.append(img)
        book_to_string.append(buy_link)
        book_to_string.append(buy_link2)
        book_to_string.append(dsc)
        book_to_string.append(book_id)
        return book_to_string
    else:
        logging.warning(f'Status Code: {query.status_code}')
        return 'Error'


def change_page(config, message_id, chat_id, wish):
    page_number = BotDB.get_page_number(message_id)
    util_id = BotDB.get_util_id(message_id)
    if wish:
        book_titles = BotDB.get_wish_title2(chat_id, util_id)
    else:
        book_titles = BotDB.get_book_title_data(util_id, chat_id)
    if config == '+':
        if len(book_titles) // 10 > page_number:
            page_number += 1
            BotDB.update_util_data(message_id, page_number)
    elif config == '-':
        if page_number > 0:
            page_number -= 1
            BotDB.update_util_data(message_id, page_number)
    elif config == '=':
        return page_number
