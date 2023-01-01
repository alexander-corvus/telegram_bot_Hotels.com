from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from loader import bot

quant_city = range(1, 11)
quant_photo = range(1, 6)


def one_choice() -> ReplyKeyboardMarkup:
    """
    Создает виртуальную клавиатуру с вариантами ответов "Да" и "Нет".
    :return: виртуальная клавиатура
    """
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    yes = KeyboardButton('да')
    no = KeyboardButton('нет')
    markup.add(yes, no)

    return markup


def yes_no(f_message: Message) -> Message:
    """
    Запрос о необходимости вывода фото отелей. Предоставляем пользователю выбор "Да" или "Нет" при помощи
    виртуальной клавиатуры.
    """

    answer = bot.send_message(f_message.chat.id, 'Показывать ли фото отелей?', reply_markup=one_choice())

    return answer


def choice_city(f_call: CallbackQuery) -> Message:
    """
    Запрос количества отелей, выводимых в одном сообщении. Предоставляем пользователю выбор от 1 до 10 вариантов
    при помощи виртуальной клавиатуры.
    :param f_call: Предыдущее сообщение от пользователя.
    :return: Вопрос пользователю.
    """
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    for num in quant_city:
        markup.add(str(num))

    answer = bot.send_message(f_call.message.chat.id, 'Сколько отелей показать за один раз?', reply_markup=markup)

    return answer


def choice_photo(f_message: Message) -> Message:
    """
    Запрос количества фото, выводимых для каждого отеля. Предоставляем пользователю выбор от 1 до 5 фото
    при помощи виртуальной клавиатуры.
    :param f_message: Предыдущее сообщение от пользователя.
    :return: Вопрос пользователю.
    """
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)

    for num in quant_photo:
        markup.add(str(num))

    answer = bot.send_message(f_message.chat.id, 'Сколько фото вывести в результатах поиска?', reply_markup=markup)

    return answer
