TOKEN = '5384713662:AAGzANRwxyOW5Wi_C1zldzZlcndRkJMAPmM'
HEROKU_APP_NAME = 'telegram-book-mate-bot'
# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 8000
