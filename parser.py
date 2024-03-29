import logging
import random
import json

import requests
from bs4 import BeautifulSoup
from create_bot import BotDB
from utils import book_parse_ua, book_parse_ru, headers, del_bounds


# Random Book
def get_random_book_from_file(lang):
    if lang == 'ru':
        random_book = random.randint(0, 98)
        file_path = 'json/top_books.json'
    else:
        random_book = random.randint(0, 117)
        file_path = 'json/top_books_ua.json'
    try:
        with open(file_path) as f:
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
    except FileNotFoundError:
        return None


def get_book_description(book_index):
    with open('json/top_books.json') as f:
        data = json.loads(f.read())
    description = data[book_index]['description']
    return description


# Book Series
def get_series_from_file(message_id, empty_array):
    try:
        util_id = BotDB.get_util_id(message_id)
    except TypeError:
        BotDB.add_util_data(message_id)
    page_number = BotDB.get_page_number(message_id)
    temp = 10
    result = ''
    if page_number == 2:
        temp = 5
    empty_array.append(temp)
    try:
        with open('json/all_series.json') as f:
            data = json.loads(f.read())
            for i in range(0, temp):
                result += f'{i + 1}. {data[i + page_number * 10]["name"]}\n'
        return result
    except FileNotFoundError:
        return None


def get_series_info(index, message_id, chat_id, empty_array):
    page_number = BotDB.get_page_number(message_id)
    with open('json/all_series.json') as f:
        data = json.loads(f.read())
        number = data[index + page_number * 10]['index']
        query = requests.get(url=data[index + page_number * 10]['link'], headers=headers)
        if query.status_code == 200:
            result = query.content
            soup = BeautifulSoup(result, 'html.parser')
            series_list = soup.find_all('div', class_='book-group-books')
            series_books = series_list[number].find_all('div', class_='book item')
            BotDB.update_util_data(message_id, 0)
            util_id = BotDB.get_util_id(message_id)
            empty_array.append(util_id)
            for j in range(0, len(series_books)):
                tmp = series_books[j].find('a', class_='title-link d-inline-block mt-2')
                book_links_temp = f'https://readrate.com{tmp.get("href")}'
                book_titles_temp = tmp.get_text()
                try:
                    book_authors_temp = series_books[j].find('a', class_='text-gray font-size-sm').get_text()
                except AttributeError:
                    book_authors_temp = 'None'
                BotDB.add_book_data(message_id, chat_id, util_id, book_titles_temp, book_authors_temp, book_links_temp)
            return True
        else:
            return False


# Book Download
def get_book_fl(title):
    url = f'https://flibusta.site/booksearch?ask={title}'
    query = requests.get(url=url, headers=headers)
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
        query = requests.get(url=download_link, headers=headers)
        file_path = 'user_book/book.fb2'
        with open(file_path, 'wb') as f:
            f.write(query.content)
        return file_path
    else:
        logging.warning(f'Status Code: {query.status_code}')
        return 'Error'


def author_search_ua(name, message_id, chat_id):
    url = f'https://www.yakaboo.ua/ua/search/author/?q={name}'
    query = requests.get(url=url, headers=headers)
    if query.status_code == 200:
        result = query.content
        soup = BeautifulSoup(result, 'html.parser')
        no_result = soup.find('div', class_='block-content').find('li')
        if no_result is None:
            return False
        BotDB.add_util_data(message_id)
        util_id = BotDB.get_util_id(message_id)
        author_info = soup.find('div',class_='unit__content').find_all('div', class_='caption')
        if len(author_info) < 10:
            count = len(author_info)
        else:
            count = 10
        # for i in range(0, count):
        i = 0
        while True:
            author_link = author_info[i].find('a', class_='product-author').get('href')
            author_name = author_info[i].find('a', class_='product-author').get_text()
            try:
                tmp_count = author_info[i].find('span', class_='amount').get_text()
            except AttributeError:
                count += 1
                i += 1
                continue
            books_count = int(del_bounds(tmp_count))
            if books_count > 20:
                books_count = f'{20} книг'
            else:
                books_count = f'{books_count} книг'
            BotDB.add_author_data(chat_id, util_id, author_name, books_count, author_link)
            i += 1
            if i >= count:
                break
        return True
    else:
        logging.warning(f'Status Code: {query.status_code}')
        return False


# Author Search
def author_search(name, message_id, chat_id):
    url = f'https://readrate.com/rus/search/authors?q={name}'
    query = requests.get(url=url, headers=headers)
    if query.status_code == 200:
        result = query.content
        soup = BeautifulSoup(result, 'html.parser')
        try:
            count = int(soup.find('span', class_='current py-2 px-3 rounded d-inline-block').find('span').get_text())
            logging.info(f'Number of books: {count}')
        except:
            return False
        authors = soup.find_all('div', class_='item ml-3 ml-md-4')
        count = 10
        if len(authors) < 10:
            count = len(authors)
        BotDB.add_util_data(message_id)
        util_id = BotDB.get_util_id(message_id)
        for i in range(0, count):
            tmp = authors[i].find('a', class_='d-block text-yellow text-decoration-underline')
            author_link = f'https://readrate.com/{tmp.get("href")}'
            author_name = authors[i].find('a', class_='d-block text-yellow text-decoration-underline').get_text()
            books_count = authors[i].find('div', class_='text-gray font-size-xs mt-1 mb-2').get_text().strip()
            temp = books_count.split(' ')
            if int(temp[0]) > 20:
                books_count = f'{20} книг'
            BotDB.add_author_data(chat_id, util_id, author_name, books_count, author_link)
        return True
    else:
        logging.warning(f'Status Code: {query.status_code}')
        return False


def get_author_book(n, message_id, chat_id, empty_array):
    util_id = BotDB.get_util_id(message_id)
    name = BotDB.get_author_data(chat_id, util_id)
    author_link = BotDB.get_author_link(chat_id, util_id, name[n - 1][0])
    query = requests.get(url=author_link, headers=headers)
    if query.status_code == 200:
        result = query.content
        soup = BeautifulSoup(result, 'html.parser')
        author_books = soup.find_all('div', class_='book item')
        BotDB.add_util_data(message_id)
        util_id = BotDB.get_util_id(message_id)
        empty_array.append(util_id)
        for j in range(0, len(author_books)):
            tmp = author_books[j].find('a', class_='title-link d-inline-block my-2')
            book_links_temp = f'https://readrate.com/{tmp.get("href")}'
            book_titles_temp = tmp.get_text()
            book_authors_temp = name[n - 1][0]
            BotDB.add_book_data(message_id, chat_id, util_id, book_titles_temp, book_authors_temp, book_links_temp)
        return True
    else:
        return False


def get_author_book_ua(n, message_id, chat_id, empty_array):
    util_id = BotDB.get_util_id(message_id)
    name = BotDB.get_author_data(chat_id, util_id)
    author_link = BotDB.get_author_link(chat_id, util_id, name[n - 1][0])
    query = requests.get(url=author_link, headers=headers)
    if query.status_code == 200:
        result = query.content
        soup = BeautifulSoup(result, 'html.parser')
        author_books = soup.find_all('li', class_='item last')
        BotDB.add_util_data(message_id)
        util_id = BotDB.get_util_id(message_id)
        empty_array.append(util_id)
        for j in range(0, len(author_books)):
            book_links_temp = author_books[j].find('a', class_='thumbnail product-image').get('href')
            book_titles_temp = author_books[j].find('a', class_='product-name').find('div',
                                                                                     class_='name').get_text().strip()
            book_authors_temp = name[n - 1][0]
            BotDB.add_book_data(message_id, chat_id, util_id, book_titles_temp, book_authors_temp, book_links_temp)
        return True
    else:
        return False


def book_search_ua(title, message_id, chat_id):
    logging.info(f'Searching: {title}')
    url = f'https://www.yakaboo.ua/ua/search?cat=4723&multi=0&q={title}'
    query = requests.get(url=url, headers=headers)
    BotDB.add_util_data(message_id)
    book_authors_temp = ''
    book_titles_temp = ''
    book_links_temp = ''
    util_id = BotDB.get_util_id(message_id)
    if query.status_code == 200:
        result = query.content
        soup = BeautifulSoup(result, 'html.parser')
        no_result = soup.find('div', class_='search-result no-result')
        if no_result is not None:
            return False
        # page books count
        items = soup.find_all('li', class_='item last')
        for j in range(0, len(items)):
            book_links_temp = items[j].find('a', class_='thumbnail product-image').get('href')
            book_titles_temp = items[j].find('a', class_='product-name').find('div',
                                                                              class_='name').get_text().strip()
            try:
                book_authors_temp = items[j].find('div', class_='product-author').get_text().strip()
            except AttributeError:
                continue
            BotDB.add_book_data(message_id, chat_id, util_id, book_titles_temp, book_authors_temp, book_links_temp)
        return True

    else:
        logging.warning(f'Status Code: {query.status_code}')
        return False


# Title Search
def book_search(title, message_id, chat_id):
    logging.info(f'Searching: {title}')
    url = f'https://readrate.com/rus/search/books?q={title}'
    query = requests.get(url=url, headers=headers)
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
            query = requests.get(url=url, headers=headers)
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
    else:
        logging.warning(f'Status Code: {query.status_code}')
        return False


# Make List Message
def make_message_authors(empty_array, message_id, chat_id):
    util_id = BotDB.get_util_id(message_id)
    author_data = BotDB.get_author_data(chat_id, util_id)
    empty_array.append(len(author_data))
    result = ''
    for author in author_data:
        result += f'{author_data.index(author) + 1}. {author[0]} - {author[1]}\n'
    return result


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


# Make book message
def get_one_book(url_book, message_id, chat_id, config):
    book_to_string = []
    if config:
        book_links = BotDB.get_wish_link(chat_id)
        book_ids = BotDB.get_wish_book_id(chat_id)
        book_id = book_ids[url_book][0]
    else:
        util_id = BotDB.get_util_id(message_id)
        book_links = BotDB.get_book_link_data(util_id, chat_id)
        book_ids = BotDB.get_book_id(util_id, chat_id)
        book_id = book_ids[url_book][0]
    book_url = book_links[url_book][0]
    query = requests.get(url=book_url, headers=headers)
    if query.status_code == 200:
        result = query.content
        soup = BeautifulSoup(result, 'html.parser')
        current_lang = BotDB.get_user_lang(chat_id)
        if current_lang == 'ru':
            book = book_parse_ru(soup)
        else:
            book = book_parse_ua(soup, book_url)
        book_to_string.append(book[0])
        book_to_string.append(book[1])
        book_to_string.append(book[2])
        book_to_string.append(book[7])
        book_to_string.append(book[5])
        book_to_string.append(book[3])
        book_to_string.append(book[4])
        book_to_string.append(book[6])
        book_to_string.append(book_id)
        return book_to_string
    else:
        logging.warning(f'Status Code: {query.status_code}')
        return 'Error'


# Change page
def change_page(config, message_id, chat_id, search_type):
    page_number = BotDB.get_page_number(message_id)
    util_id = BotDB.get_util_id(message_id)
    if search_type == 'wish':
        book_titles = BotDB.get_wish_title2(chat_id, util_id)
    else:
        book_titles = BotDB.get_book_title_data(util_id, chat_id)
    if search_type == 'series':
        elements_count = 25
    else:
        elements_count = len(book_titles)
    if config == '+':
        if elements_count // 10 > page_number and not (
                elements_count % 10 == 0 and elements_count // 10 == page_number + 1):
            page_number += 1
            BotDB.update_util_data(message_id, page_number)
    elif config == '-':
        if page_number > 0:
            page_number -= 1
            BotDB.update_util_data(message_id, page_number)
    elif config == '=':
        return page_number
