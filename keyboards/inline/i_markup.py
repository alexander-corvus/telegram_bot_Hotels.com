from typing import Any
from loader import MyStates
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def choice_city(f_data: Any) -> InlineKeyboardMarkup:
    """
    Создание inline-клавиатуры с вариантами городов. Поиск через API на Hotels.com.
    """
    markup = InlineKeyboardMarkup(row_width=1)

    for elem in f_data['sr']:
        if elem['type'] == 'CITY':
            button_name = elem['regionNames']['displayName']
            destination_id = elem['gaiaId']

            translation = {39: None}
            button = InlineKeyboardButton(f"{button_name}".translate(translation),
                                          callback_data=f'{destination_id }')
            markup.add(button)

            MyStates.dict_of_results[destination_id] = button_name

    return markup
