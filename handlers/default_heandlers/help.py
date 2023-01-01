from loader import bot
from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from database.funcs_of_database import rec_command


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    """
    Команда, показывающая подсказку пользователю.
    """

    rec_command(message, 'help')

    def_commands = [f'/{command} - {description}' for command, description in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(def_commands))
