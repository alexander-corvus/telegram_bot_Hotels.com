import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPIDAPI_KEY')

DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('lowprice', "Вывод самых дешевых отелей в городе"),
    ('highprice', "Вывод самых дорогих отелей в городе"),
    ('bestdeal', "Вывод лучших предложений цена / расположение"),
    ('history', "Вывод истории поиска отелей")
)
