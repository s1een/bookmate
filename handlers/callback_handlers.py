from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

from create_bot import dp, bot
from ui.kayboard import *
from main import get_dsc, get_book_fl, get_one_book, make_message_book, change_page
from create_bot import BotDB


# Add book to WishList
@dp.callback_query_handler(text="wishlist")
async def add_to_wishlist(call: types.CallbackQuery):
    book_id = BotDB.get_help_book_id(call.message.message_id, call.message.chat.id)
    one_book = BotDB.get_book_info(book_id)
    BotDB.add_book_to_wishlist(call.message.chat.id, one_book[0], one_book[1], one_book[2])
    await call.answer('Book has been added to wishlist.')


# Book Description
@dp.callback_query_handler(text=["book info", 'book_info_wish', 'dsc'])
async def get_description_search(call: types.CallbackQuery):
    if call.data == 'book info':
        book_description = BotDB.get_description_bd(call.message.message_id, call.message.chat.id)
        await call.message.answer(book_description)
        book_link = BotDB.get_help_book_link(call.message.message_id, call.message.chat.id)
        temp = ''
        await call.message.edit_caption(call.message.caption,
                                        reply_markup=create_main_board(temp.join(book_link[0]), temp.join(book_link[1]),
                                                                       'add_to_wish'))
    elif call.data == 'book_info_wish':
        book_description = BotDB.get_description_bd(call.message.message_id, call.message.chat.id)
        await call.message.answer(book_description)
    else:
        k = call.message.caption.split(' ')
        st = get_dsc(int(k[1]))
        await call.message.answer(st.strip())


# Book Download
@dp.callback_query_handler(text=['download', 'top download'])
async def download_book(call: types.CallbackQuery):
    await call.message.answer('Searching...')
    if call.data.startswith('top'):
        k = call.message.caption.split('\n')
        z = k[1].split(':')
    else:
        k = call.message.caption.split('\n')
        z = k[0].split(':')
    tm = ''
    if len(z) > 2:
        for i in range(1, len(z)):
            tm += z[i]
    else:
        tm = z[1]
    k = get_book_fl(tm.strip())
    if k == 'Error':
        await call.message.answer('I have not found such a book.')
    else:
        await call.message.answer_document(open(k, 'rb'))


# Next button
@dp.callback_query_handler(text=['next', 'wish next'])
async def get_search_book(call: types.CallbackQuery):
    mas = []
    if call.data.startswith('wish'):
        change_page('+', call.message.message_id, call.message.chat.id, True)
        try:
            await bot.edit_message_text(
                make_message_book(mas, call.message.message_id, call.message.chat.id, True).strip(),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_inline_wish(mas[0]))
        except MessageNotModified:
            await call.answer('Its last page')
    else:
        change_page('+', call.message.message_id, call.message.chat.id, False)
        try:
            await bot.edit_message_text(
                make_message_book(mas, call.message.message_id, call.message.chat.id, False).strip(),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_inline(mas[0]))
        except MessageNotModified:
            await call.answer('Its last page')


# Back Button
@dp.callback_query_handler(text=['back', 'wish back'])
async def get_search_book(call: types.CallbackQuery):
    mas = []
    if call.data.startswith('wish'):
        change_page('-', call.message.message_id, call.message.chat.id, True)
        try:
            await bot.edit_message_text(
                make_message_book(mas, call.message.message_id, call.message.chat.id, True).strip(),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_inline_wish(mas[0]))
        except MessageNotModified:
            await call.answer('Its first page')
    else:
        change_page('-', call.message.message_id, call.message.chat.id, False)
        try:
            await bot.edit_message_text(
                make_message_book(mas, call.message.message_id, call.message.chat.id, False).strip(),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_inline(mas[0]))
        except MessageNotModified:
            await call.answer('Its first page')


# Get Book
@dp.callback_query_handler()
async def get_search_book(call: types.CallbackQuery):
    await call.message.answer('Searching...')
    if call.data.startswith('wishbook'):
        k = call.data.split(' ')
        page = change_page('=', call.message.message_id, call.message.chat.id, True)
        p = int(k[1]) - 1 + page * 10
        book = get_one_book(p, call.message.message_id, call.message.chat.id, True)
        if book != 'Error':
            result = f'\n*Title:* _{book[0]}_ ' \
                     f'\n*Author:* _{book[1]}_ ' \
                     f'\n*Genre:* _{book[2]}_ ' \
                     f'\n*Stars:* _{book[3]}_ \n'
            board = create_main_board(book[5], book[6], 'wishlist')
            temp = await bot.send_photo(call.from_user.id, book[4],
                                        caption=result,
                                        parse_mode=types.ParseMode.MARKDOWN,
                                        reply_markup=board)
            BotDB.add_book_help(temp.chat.id, temp.message_id, book[7], book[5], book[6], book[8])
        else:
            await call.answer('Page not available.')
    else:
        k = call.data.split(' ')
        page = change_page('=', call.message.message_id, call.message.chat.id, False)
        p = int(k[1]) - 1 + page * 10
        book = get_one_book(p, call.message.message_id, call.message.chat.id, False)
        if book != 'Error':
            result = f'\n*Title:* _{book[0]}_ ' \
                     f'\n*Author:* _{book[1]}_ ' \
                     f'\n*Genre:* _{book[2]}_ ' \
                     f'\n*Stars:* _{book[3]}_ \n'
            board = create_main_board(book[5], book[6], 'main')
            temp = await bot.send_photo(call.from_user.id, book[4],
                                        caption=result,
                                        parse_mode=types.ParseMode.MARKDOWN,
                                        reply_markup=board)
            BotDB.add_book_help(temp.chat.id, temp.message_id, book[7], book[5], book[6], book[8])
        else:
            await call.answer('Page not available.')
