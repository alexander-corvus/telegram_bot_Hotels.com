from loader import bot
from telebot.types import Message
from states.user_states import MyStates
from utils.misc.templates_of_strings import greetings_start
from database.funcs_of_database import rec_command


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """
    Команда START, запускающая бота.
    Функция также сохраняет ID пользователя.
    """
    MyStates.dict_of_results.clear()
    MyStates.user_id = message.from_user.id

    rec_command(message, 'start')

    bot.send_message(message.chat.id,
                     greetings_start.format(
                      username=message.from_user.full_name))
