import random

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode, ReplyKeyboardRemove, ContentType
from aiogram.utils.markdown import text, bold, italic

from create_bot import dp, bot, Form, cats, BotDB
from ui.kayboard import markup, create_inline, create_inline_wish, create_main_board
from main import get_random_book_from_file, book_search, make_message_book


# Start Message
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    if not BotDB.user_exist(message.from_user.id):
        BotDB.add_user(message.from_user.id, message.from_user.first_name)
    await message.answer(f"Hello, {message.from_user.get_mention(as_html=True)} 👋!",
                         parse_mode=types.ParseMode.HTML, reply_markup=markup)


# Get All Commands
@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    msg = text(bold('I can respond to the following commands:'),
               '/start - start interaction with the bot.',
               '/help - get user manual.',
               '/rbook - random book.',
               '/blist - get a directory.',
               '/mybooks - wishlist.',
               '/dev - test command.',
               '/cats - get cats.',
               '/file - test command.', sep='\n')
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN)


# Get a Random Book from Top 100
@dp.message_handler(Text(equals='Random Book'))
@dp.message_handler(commands=['rbook'])
async def process_rbook_command(message: types.Message):
    book = get_random_book_from_file()
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


# Book Search Start
@dp.message_handler(commands=['search'])
@dp.message_handler(Text(equals='Search'))
async def process_search_command(message: types.Message):
    await Form.book.set()
    await message.answer('Enter book name to search..')


# State Cancel
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='Back to Menu', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


# Book Search by Name
@dp.message_handler(state=Form.book)
async def answer_bot(message: types.Message, state: FSMContext):
    await message.answer('Wait...')
    title_text = message.text
    result = book_search(title_text, message.message_id, message.chat.id)
    mas = []
    util_id = BotDB.get_util_id(message.message_id)
    if result is True:
        bot_message = await bot.send_message(message.chat.id,
                                             make_message_book(mas, message.message_id, message.chat.id, False).strip(),
                                             reply_markup=create_inline(mas[0]))
        BotDB.update_util_message_id(util_id, bot_message.message_id)
    else:
        await message.answer('No matches were found for your query.')
    await state.finish()


# Delete Keyboard
@dp.message_handler(commands=['rm'])
async def process_rm_command(message: types.Message):
    await message.answer("Your keyboard was deleted", reply_markup=ReplyKeyboardRemove())


# Get WishList
@dp.message_handler(commands=['mybooks'])
@dp.message_handler(Text(equals="Wishlist"))
async def process_mybooks_command(message: types.Message):
    mas = []
    result = make_message_book(mas, message.message_id, message.chat.id, True)
    if result != '':
        bot_message = await bot.send_message(message.chat.id,
                                             result.strip(),
                                             reply_markup=create_inline_wish(mas[0]))
        util_id = BotDB.get_util_id(message.message_id)
        BotDB.update_util_message_id(util_id, bot_message.message_id)
    else:
        await message.answer('Your wish list is empty.')


# Cats Command Handler
@dp.message_handler(commands=['cats'])
async def process_cats_command(message: types.Message):
    caption = 'Вредина. 🖤 ♥'
    random_path = random.choice(cats)
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


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(process_start_command, commands=['start'])
    dp.register_message_handler(process_help_command, commands=['help'])
    dp.register_message_handler(process_rbook_command, commands=['rbook'])
    dp.register_message_handler(process_search_command, commands=['search'])
    dp.register_message_handler(process_cats_command, commands=['cats'])
