from peewee import *
import os

# Команда, которую вводил пользователь.
# Дата и время ввода команды.
# Отели, которые были найдены.

path_to_db = os.path.join('database', 'history.db')
db = SqliteDatabase(path_to_db)


class CommandsData(Model):
    """
    Класс для формирования данных первой таблицы в DB.
    """
    userid = IntegerField()
    command = TextField()
    date_of_input = DateField()
    time_of_input = TimeField()

    class Meta:
        database = db


class HotelsData(Model):
    """
    Класс для формирования данных второй таблицы в DB.
    """
    userid = IntegerField()
    hotel = TextField()

    class Meta:
        database = db


CommandsData.create_table()
HotelsData.create_table()
