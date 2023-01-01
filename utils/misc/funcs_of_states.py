from typing import Any
from loader import bot, storage, MyStates
from telebot.types import Message, CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import datetime
import re

date_today = datetime.now().date()
calendar, step = DetailedTelegramCalendar(min_date=date_today).build()
start = f"Выберите дату начала поездки: {LSTEP[step]}"
stop = f'Теперь укажите дату выезда: {LSTEP[step]}'

end_text: str = '\nВсе правильно?'


def answer_end_states(f_states_dict: dict) -> str:
    """
    Заполнение пользовательского класса для дальнейшей работы команд.
    Вывод данных о пользователе, полученных по итогам опроса.
    """
    MyStates.dict_of_results['city'] = f_states_dict["city"]
    MyStates.dict_of_results['city_id'] = f_states_dict["city_id"]
    MyStates.dict_of_results['checkin_tpl'] = tuple(map(int, str(f_states_dict["check_in"]).split('-')))
    MyStates.dict_of_results['checkout_tpl'] = tuple(map(int, str(f_states_dict["check_out"]).split('-')))
    MyStates.dict_of_results['results_size'] = int(f_states_dict['hotels_count'])

    f_answer = (f'\nИтак, вот эти данные использую для поиска:\n'
                f'Город: {MyStates.dict_of_results["city"]}\n'
                f'Дата заезда: {f_states_dict["check_in"]}\n'
                f'Дата выезда: {f_states_dict["check_out"]}\n'
                f'Количество вариантов отелей в одном ответе: {MyStates.dict_of_results["results_size"]}\n'
                f'Показ фото: {f_states_dict["photo_check"]}\n')

    return f_answer


def context_states(f_message: Message, f_state: str) -> None:
    """
    Контекстный менеджер для сохранения данных о пользователе в класс пользовательских состояний
    для типа данных Message.
    """
    with bot.retrieve_data(f_message.from_user.id, f_message.chat.id) as data:
        data[f_state] = f_message.text


def context_states_call(f_call: CallbackQuery, f_state: str, f_data: str) -> None:
    """
    Контекстный менеджер для сохранения данных о пользователе в класс пользовательских состояний
    для типа данных CallbackQuery.
    """
    with bot.retrieve_data(f_call.from_user.id, f_call.message.chat.id) as data:
        data[f_state] = f_data


def my_calendar(f_call: CallbackQuery, f_text: str) -> None:
    bot.send_message(f_call.message.chat.id, f_text, reply_markup=calendar)


def states_dict() -> dict:
    """
    Функция, возвращающая пользовательские данные в виде словаря.
    Работает только после опроса пользователя.
    """
    return storage.data[MyStates.user_id][MyStates.user_id]['data']


def get_state_data(state_name: str) -> Any:
    """
    Функция, возвращающая значение определенной стадии.
    Работает только после опроса пользователя
    """
    return states_dict()[state_name]


def cyrillic(text: str) -> bool:
    """
    Функция, проверяющая наличие русских букв в тексте.
    """
    return bool(re.search('[а-яА-Я]', text))
