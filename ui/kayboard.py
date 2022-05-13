from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# Keyboard
def main_keyboard():
    button1 = KeyboardButton('Search')
    button2 = KeyboardButton('Random Book')
    button3 = KeyboardButton('Wishlist')
    button4 = KeyboardButton('Back to Menu')

    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        button1).insert(button2).add(button3).insert(button4)
    return markup


def search_keyboard():
    button1 = KeyboardButton('Book')
    button2 = KeyboardButton('Author')
    button3 = KeyboardButton('Series')
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        button1).insert(button2).insert(button3)
    return markup


# Inline
def create_inline(count,status):
    kb = InlineKeyboardMarkup(row_width=5)
    if count > 0:
        book_button1 = InlineKeyboardButton('1', callback_data=f'{status} 1')
        kb.add(book_button1)
    if count > 1:
        book_button2 = InlineKeyboardButton('2', callback_data=f'{status} 2')
        kb.insert(book_button2)
    if count > 2:
        book_button3 = InlineKeyboardButton('3', callback_data=f'{status} 3')
        kb.insert(book_button3)
    if count > 3:
        book_button4 = InlineKeyboardButton('4', callback_data=f'{status} 4')
        kb.insert(book_button4)
    if count > 4:
        book_button5 = InlineKeyboardButton('5', callback_data=f'{status} 5')
        kb.insert(book_button5)
    if count > 5:
        book_button6 = InlineKeyboardButton('6', callback_data=f'{status} 6')
        kb.insert(book_button6)
    if count > 6:
        book_button7 = InlineKeyboardButton('7', callback_data=f'{status} 7')
        kb.insert(book_button7)
    if count > 7:
        book_button8 = InlineKeyboardButton('8', callback_data=f'{status} 8')
        kb.insert(book_button8)
    if count > 8:
        book_button9 = InlineKeyboardButton('9', callback_data=f'{status} 9')
        kb.insert(book_button9)
    if count > 9:
        book_button10 = InlineKeyboardButton('10', callback_data=f'{status} 10')
        kb.insert(book_button10)
    if status == 'author':
        return kb
    back_button = InlineKeyboardButton('<-', callback_data=f'{status} back')
    next_button = InlineKeyboardButton('->', callback_data=f'{status} next')
    kb.add(back_button).insert(next_button)
    return kb

def create_main_board(first_store, second_store, config):
    inline_btn_store1 = InlineKeyboardButton('EBook', callback_data='store', url=first_store)
    inline_btn_store2 = InlineKeyboardButton('Download', callback_data='download')
    inline_btn_store3 = InlineKeyboardButton('Paper book', callback_data='store3', url=second_store)
    inline_dsc_btn = InlineKeyboardButton('Description!', callback_data='book info')
    if config == 'top':
        inline_btn_store2 = InlineKeyboardButton('Download', callback_data='top download')
        inline_dsc_btn = InlineKeyboardButton('Description!', callback_data='dsc')
    elif config == 'add_to_wish':
        inline_dsc_btn = InlineKeyboardButton('Add To Wishlist!', callback_data='wishlist')
    elif config == 'wishlist':
        inline_dsc_btn = InlineKeyboardButton('Description!', callback_data='book_info_wish')

    inline_kb = InlineKeyboardMarkup().add(inline_dsc_btn).add(inline_btn_store1) \
        .insert(inline_btn_store2).insert(inline_btn_store3)
    return inline_kb
