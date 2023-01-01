from telebot.types import Message
from loader import bot
from database.base import CommandsData, HotelsData
from database.funcs_of_database import rec_command


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    """
    Функция выводит пользователю историю вводимых команд и просмотренные отели.
    """

    rec_command(message, 'history')

    bot.send_message(message.chat.id, '\n<b>Введенные команды:</b>\n', parse_mode='html')
    for command in CommandsData.select():
        if message.from_user.id == command.userid:
            bot.send_message(message.chat.id, f'{command.date_of_input}, '
                                              f'{command.time_of_input}, '
                                              f'команда {command.command}\n')

    bot.send_message(message.chat.id, '\n<b>Просмотренные отели:</b>\n', parse_mode='html')
    for hotel in HotelsData.select():
        if message.from_user.id == hotel.userid:
            bot.send_message(message.chat.id, hotel.hotel)

    bot.send_message(message.chat.id, '<pre>Вывод истории поиска завершен.\n'
                                      'Для просмотра доступных команд нажми</pre> /help',
                     parse_mode='html')
