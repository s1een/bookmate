import random

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode, ReplyKeyboardRemove, ContentType
from aiogram.utils.markdown import text, bold, italic

from create_bot import dp, bot, Form, cats, BotDB
from ui.keyboard import *
from parser import *


# Start Message
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer_chat_action('choose_sticker')
    if not BotDB.user_exist(message.from_user.id):
        BotDB.add_user(message.from_user.id, message.from_user.first_name, 'choice')
    await message.answer(f"Hello, {message.from_user.get_mention(as_html=True)} 👋!",
                         parse_mode=types.ParseMode.HTML, reply_markup=main_keyboard())


# Get All Commands
@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    msg = text(bold('I can respond to the following commands:'),
               '/start - start interaction with the bot.',
               '/help - get user manual.',
               '/search - search mode.',
               '/choice - default search mode.',
               '/book - title search mode.',
               '/author - author search mode.',
               '/series - series search mode.',
               '/rbook - random book.',
               '/mybooks - wishlist.',
               '/rmybooks - delete from wishlist.', sep='\n')
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN)


# Get a Random Book from Top 100
@dp.message_handler(Text(equals='Random Book'))
@dp.message_handler(commands=['rbook'])
async def process_rbook_command(message: types.Message):
    book = get_random_book_from_file()
    if book is not None:
        result = f'*№* _{book[0]}_ ' \
                 f'\n*Title:* _{book[1]}_ ' \
                 f'\n*Author:* _{book[2]}_ ' \
                 f'\n*Genre:* _{book[3]}_ ' \
                 f'\n*Stars:* _{book[4]}_ \n'
        board = create_main_board(book[6], book[7], 'top')
        await bot.send_photo(message.from_user.id, book[5],
                             caption=result,
                             parse_mode=types.ParseMode.MARKDOWN,
                             reply_markup=board)
    else:
        await message.answer('Error, please try later. 😔')


# Get WishList
@dp.message_handler(commands=['mybooks'])
@dp.message_handler(Text(equals="Wishlist"))
async def process_mybooks_command(message: types.Message):
    mas = []
    result = make_message_book(mas, message.message_id, message.chat.id, True)
    if result != '':
        bot_message = await bot.send_message(message.chat.id,
                                             result.strip(),
                                             reply_markup=create_inline(mas[0], 'wishlist'))
        util_id = BotDB.get_util_id(message.message_id)
        BotDB.update_util_message_id(util_id, bot_message.message_id)
    else:
        await message.answer('Your wish list is empty.')


@dp.message_handler(Text(equals="Remove book from wishlist"))
async def process_rmybooks_command(message: types.Message):
    mas = []
    result = make_message_book(mas, message.message_id, message.chat.id, True)
    if result != '':
        bot_message = await bot.send_message(message.chat.id,
                                             result.strip(),
                                             reply_markup=create_inline(mas[0], 'delete'))
        util_id = BotDB.get_util_id(message.message_id)
        BotDB.update_util_message_id(util_id, bot_message.message_id)
    else:
        await message.answer('Your wish list is empty.')


# Book Search Start
@dp.message_handler(commands=['search'])
@dp.message_handler(Text(equals='Search'))
async def process_search_command(message: types.Message, state: FSMContext):
    user_status = BotDB.get_user_status(message.chat.id)
    if user_status == 'choice':
        await Form.choice.set()
        await message.answer('Choice search type..', reply_markup=search_keyboard())
    elif user_status == 'book':
        await Form.book.set()
        await message.answer('Enter book name to search..')
    elif user_status == 'author':
        await Form.author.set()
        await message.answer('Enter book author to search..')
    elif user_status == 'series':
        await message.answer_chat_action('typing')
        await message.answer('Searching..', reply_markup=main_keyboard())
        await answer_series(message, state)


# State Cancel
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals=['Wishlist', 'Random Book', 'Search','Remove book from wishlist'], ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Cancelled.')


# Choice commands
@dp.message_handler(commands=['choice'])
async def process_choice_command(message: types.Message):
    BotDB.update_status('choice', message.chat.id)
    await message.delete()
    await message.answer('Search status - choice.')


@dp.message_handler(commands=['book'])
async def process_book_command(message: types.Message):
    BotDB.update_status('book', message.chat.id)
    await message.delete()
    await message.answer('Search status - By Book name.')


@dp.message_handler(commands=['author'])
async def process_author_command(message: types.Message):
    BotDB.update_status('author', message.chat.id)
    await message.delete()
    await message.answer('Search status - By Author name.')


@dp.message_handler(commands=['series'])
async def process_series_command(message: types.Message):
    BotDB.update_status('series', message.chat.id)
    await message.delete()
    await message.answer('Search status - By Series.')


@dp.message_handler(state=Form.choice)
async def answer_choice(message: types.Message, state: FSMContext):
    msg_text = message.text
    if msg_text == 'Book':
        await Form.book.set()
        await message.answer('Enter book name to search..', reply_markup=main_keyboard())
    elif msg_text == 'Author':
        await Form.author.set()
        await message.answer('Enter book author to search..', reply_markup=main_keyboard())
    elif msg_text == 'Series':
        await message.answer('Searching..', reply_markup=main_keyboard())
        await answer_series(message, state)


# Book Search by Name
@dp.message_handler(state=Form.book)
async def answer_book(message: types.Message, state: FSMContext):
    await message.answer_chat_action('typing')
    title_text = message.text
    result = book_search(title_text, message.message_id, message.chat.id)
    mas = []
    util_id = BotDB.get_util_id(message.message_id)
    if result is True:
        bot_message = await bot.send_message(message.chat.id,
                                             make_message_book(mas, message.message_id, message.chat.id, False).strip(),
                                             reply_markup=create_inline(mas[0], 'book'))
        BotDB.update_util_message_id(util_id, bot_message.message_id)
    else:
        await message.answer('No matches were found for your query.')
    await state.finish()


# Book Search by Author
@dp.message_handler(state=Form.author)
async def answer_author(message: types.Message, state: FSMContext):
    await message.answer_chat_action('typing')
    msg_text = message.text
    result = author_search(msg_text, message.message_id, message.chat.id)
    mas = []
    if result is True:
        util_id = BotDB.get_util_id(message.message_id)
        bot_message = await bot.send_message(message.chat.id,
                                             make_message_authors(mas, message.message_id, message.chat.id).strip(),
                                             reply_markup=create_inline(mas[0], 'author'))
        BotDB.update_util_message_id(util_id, bot_message.message_id)
    else:
        await message.answer('No matches were found for your query.')
    await state.finish()


# Book Search by Series
@dp.message_handler(state=Form.series)
async def answer_series(message: types.Message, state: FSMContext):
    await message.answer_chat_action('typing')
    mas = []
    result = get_series_from_file(message.message_id, mas)
    if result is not None:
        util_id = BotDB.get_util_id(message.message_id)
        bot_message = await bot.send_message(message.chat.id, result,
                                             reply_markup=create_inline(mas[0], 'series'))
        BotDB.update_util_message_id(util_id, bot_message.message_id)
        await state.finish()
    else:
        await message.answer('Error, please try later. 😔')


# Delete Keyboard
@dp.message_handler(commands=['rm'])
async def process_rm_command(message: types.Message):
    await message.answer("Your keyboard was deleted", reply_markup=ReplyKeyboardRemove())


# Cats Command Handler
@dp.message_handler(commands=['cats'])
async def process_cats_command(message: types.Message):
    caption = 'Вредина. 🖤'
    random_path = random.choice(cats)
    await message.answer_chat_action('choose_sticker')
    with open(random_path, "rb") as file:
        await bot.send_photo(message.from_user.id, file.read(),
                             caption=caption,
                             reply_to_message_id=message.message_id)


# Unknown Message Handler
@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(message: types.Message):
    message_text = text("I don't know what to do with it :astonished:",
                        italic("\nI'll just remind you that there is a command /help"))
    await message.reply(message_text, parse_mode=ParseMode.MARKDOWN)
