import datetime
from database.base import CommandsData, HotelsData
from telebot.types import Message


def date_time(f_now: datetime) -> tuple:
    """
    Функция, возвращающая кортеж, состоящий из текущих даты и времени.
    """

    year = f_now.year
    month = f_now.month
    day = f_now.day
    now_date = datetime.date(year, month, day)

    hour = f_now.hour
    minute = f_now.minute
    second = f_now.second
    now_time = datetime.time(hour, minute, second)

    return now_date, now_time


def rec_command(message: Message, command: str) -> None:
    """
    Функция записи в DB данных о командах, введенных пользователем.
    """
    now = datetime.datetime.now()

    CommandsData.create(userid=message.from_user.id,
                        command=command,
                        date_of_input=date_time(now)[0],
                        time_of_input=date_time(now)[1])


def rec_hotel(message: Message, hotelname: str) -> None:
    """
    Функция записи в DB названия выводимого отеля.
    """

    HotelsData.create(userid=message.from_user.id,
                      hotel=hotelname)

