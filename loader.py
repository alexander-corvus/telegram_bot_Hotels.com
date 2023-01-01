from telebot import TeleBot
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from config_data import config

storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)


class MyStates(StatesGroup):
    """
    Класс для хранения состояний пользователя.
    """
    user_id = None
    dict_of_results = {}

    command = State()

    dist_min = State()
    dist_max = State()
    price_max = State()
    price_min = State()

    city = State()
    city_id = State()
    check_in = State()
    check_out = State()
    hotels_count = State()
    photo_check = State()
    photo_count = State()
    end = State()
    choice_command = State()


class Hotel:
    """
    Класс для временного хранения данных об отелях, показанных на одной странице вывода вариантов.
    """
    def __init__(self, user_id):
        self.user_id = user_id
        self.results = {self.user_id: []}

    hotel_id: str = None
    name: str = None
    dist_center: str = None
    price_day: str = None
    price_total: str = None
    address: str = None
    link: str = None

    def rec_results(self) -> None:
        """
        Метод записи данных в словарь.
        """

        interim_dictionary = {self.hotel_id: {'hotel_name': self.name,
                                              'address': self.address,
                                              'dist_center': self.dist_center,
                                              'price_day': self.price_day,
                                              'price_total': self.price_total,
                                              'link': self.link
                                              }
                              }

        self.results[self.user_id].append(interim_dictionary)

    def get_results(self):
        """
        Метод, возвращающий словарь с данными.
        """
        return self.results
