import sqlite3


class BotDB:
    def __init__(self, db_file):
        """Connection to Data Base"""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    # USERS
    def user_exist(self, user_id):
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def add_user(self, user_id, user_name, search_status, lang):
        self.cursor.execute("INSERT INTO `users` (`id`,`user_name`,`search_status`,`language`) VALUES (?,?,?,?)",
                            (user_id, user_name, search_status, lang))
        return self.conn.commit()

    def get_user_status(self, user_id):
        result = self.cursor.execute("SELECT `search_status` FROM `users` WHERE `id` = ?", (user_id,))
        return result.fetchone()[0]

    def update_status(self, status, user_id):
        self.cursor.execute("UPDATE `users` SET `search_status` = ? WHERE `id` = ?", (status, user_id))
        return self.conn.commit()

    def get_user_lang(self, user_id):
        result = self.cursor.execute("SELECT `language` FROM `users` WHERE `id` = ?", (user_id,))
        return result.fetchone()[0]

    def update_lang(self, status, user_id):
        self.cursor.execute("UPDATE `users` SET `language` = ? WHERE `id` = ?", (status, user_id))
        return self.conn.commit()

    # UTIL_TABLE
    def add_util_data(self, message_id):
        self.cursor.execute("INSERT INTO `util_table` (`message_id`,`page_number`) VALUES (?,?)",
                            (message_id, 0))
        return self.conn.commit()

    def update_util_data(self, message_id, page_number):
        self.cursor.execute("UPDATE `util_table` SET `page_number` = ? WHERE `message_id` = ?",
                            (page_number, message_id))
        return self.conn.commit()

    def update_util_message_id(self, id, message_id):
        self.cursor.execute("UPDATE `util_table` SET `message_id` = ? WHERE `id` = ?",
                            (message_id, id))
        return self.conn.commit()

    def get_util_id(self, message_id):
        result = self.cursor.execute("SELECT `id` FROM `util_table` WHERE `message_id` = ?", (message_id,))
        return result.fetchone()[0]

    def get_page_number(self, message_id):
        result = self.cursor.execute("SELECT `page_number` FROM `util_table` WHERE `message_id` = ?", (message_id,))
        return result.fetchone()[0]

    #   USER WISHLIST
    def update_wishlist_util_id(self, util_id, chat_id):
        self.cursor.execute("UPDATE `user_wishlist` SET `util_id` = ? WHERE `chat_id` = ?",
                            (util_id, chat_id))
        return self.conn.commit()

    def get_wish_book_id(self, chat_id):
        result = self.cursor.execute("SELECT `id` FROM `user_wishlist` WHERE `chat_id` = ?",
                                     (chat_id,))
        return result.fetchall()

    def delete_wish(self, user_id, chat_id):
        self.cursor.execute("DELETE FROM `user_wishlist` WHERE `id` = ? AND `chat_id` = ?",
                            (user_id, chat_id))
        return self.conn.commit()

    def add_book_to_wishlist(self, chat_id, book_title, book_author, book_link):
        self.cursor.execute(
            "INSERT INTO `user_wishlist` (`chat_id`, `book_title`,`book_author`,`book_link`) VALUES (?,?,?,?)",
            (chat_id, book_title, book_author, book_link))
        return self.conn.commit()

    def get_wish_title(self, chat_id):
        result = self.cursor.execute("SELECT `book_title` FROM `user_wishlist` WHERE `chat_id` = ?",
                                     (chat_id,))
        return result.fetchall()

    def get_wish_title2(self, chat_id, util_id):
        result = self.cursor.execute("SELECT `book_title` FROM `user_wishlist` WHERE `chat_id` = ? and `util_id` = ?",
                                     (chat_id, util_id))
        return result.fetchall()

    def get_wish_author(self, chat_id):
        result = self.cursor.execute("SELECT `book_author` FROM `user_wishlist` WHERE `chat_id` = ?",
                                     (chat_id,))
        return result.fetchall()

    def get_wish_link(self, chat_id):
        result = self.cursor.execute("SELECT `book_link` FROM `user_wishlist` WHERE `chat_id` = ?",
                                     (chat_id,))
        return result.fetchall()

    def book_exist(self, chat_id, book_link):
        result = self.cursor.execute("SELECT `book_link` FROM `user_wishlist` WHERE `chat_id` = ? and `book_link` = ?",
                                     (chat_id, book_link))
        return bool(len(result.fetchall()))

    # BOOKS
    def add_book_data(self, message_id, chat_id, util_id, book_title, book_author, book_link):
        self.cursor.execute(
            "INSERT INTO `books` (`message_id`,`chat_id`,`util_id`,`book_titles`,`book_authors`,`book_links`) VALUES (?,?,?,?,?,?)",
            (message_id, chat_id, util_id, book_title, book_author, book_link))
        return self.conn.commit()

    def get_book_title_data(self, util_id, chat_id):
        result = self.cursor.execute("SELECT `book_titles` FROM `books` WHERE `util_id` = ? AND `chat_id` = ?",
                                     (util_id, chat_id))
        return result.fetchall()

    def get_book_author_data(self, util_id, chat_id):
        result = self.cursor.execute("SELECT `book_authors` FROM `books` WHERE `util_id` = ? AND `chat_id` = ?",
                                     (util_id, chat_id))
        return result.fetchall()

    def get_book_link_data(self, util_id, chat_id):
        result = self.cursor.execute("SELECT `book_links` FROM `books` WHERE `util_id` = ? AND `chat_id` = ?",
                                     (util_id, chat_id))
        return result.fetchall()

    def get_book_id(self, util_id, chat_id):
        result = self.cursor.execute("SELECT `id` FROM `books` WHERE `util_id` = ? AND `chat_id` = ?",
                                     (util_id, chat_id))
        return result.fetchall()

    def get_book_info(self, book_id):
        result = self.cursor.execute("SELECT `book_titles`,`book_authors`, `book_links` FROM `books` WHERE `id` = ?",
                                     (book_id,))
        return result.fetchone()

    # BOOK HELP
    def get_description_bd(self, message_id, chat_id):
        result = self.cursor.execute("SELECT `description` FROM `book_help` WHERE `chat_id` = ? AND `message_id` = ?",
                                     (chat_id, message_id,))
        return result.fetchone()[0]

    def get_help_book_link(self, message_id, chat_id):
        result = self.cursor.execute(
            "SELECT `book_link`,`book_link2` FROM `book_help` WHERE `message_id` = ? AND `chat_id` = ?",
            (message_id, chat_id))
        return result.fetchone()

    def add_book_help(self, chat_id, message_id, description, buy_link, buy_link2, book_id):
        self.cursor.execute(
            "INSERT INTO `book_help` (`chat_id`,`message_id`,`description`,`book_link`,`book_link2`,`book_id`) VALUES (?,?,?,?,?,?)",
            (chat_id, message_id, description, buy_link, buy_link2, book_id))
        return self.conn.commit()

    def get_help_book_id(self, message_id, chat_id):
        result = self.cursor.execute("SELECT `book_id` FROM `book_help` WHERE `message_id` = ? AND `chat_id` = ?",
                                     (message_id, chat_id))
        return result.fetchone()[0]

    # AUTHORS
    def add_author_data(self, chat_id, util_id, author_name, books_count, author_link):
        self.cursor.execute(
            "INSERT INTO `authors` (`chat_id`,`util_id`,`author_name`,`books_count`,`author_link`) VALUES (?,?,?,?,?)",
            (chat_id, util_id, author_name, books_count, author_link))
        return self.conn.commit()

    def get_author_data(self, chat_id, util_id):
        result = self.cursor.execute(
            "SELECT `author_name`,`books_count` FROM `authors` WHERE `chat_id` = ? and `util_id` = ?",
            (chat_id, util_id))
        return result.fetchall()

    def get_author_link(self, chat_id, util_id, author_name):
        result = self.cursor.execute(
            "SELECT `author_link` FROM `authors` WHERE `chat_id` = ? and `util_id` = ? and `author_name` = ?",
            (chat_id, util_id, author_name))
        return result.fetchone()[0]

    def close(self):
        """Disconnect from Data Base"""
        self.conn.close()
