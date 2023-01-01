from loader import bot, MyStates
from telebot.types import Message, ReplyKeyboardRemove, CallbackQuery
from utils.misc.funcs_of_states import answer_end_states, context_states, context_states_call, end_text,\
    get_state_data, states_dict, my_calendar, start, stop, date_today, cyrillic
from keyboards.reply import r_markup
from keyboards.inline.i_markup import choice_city
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from utils.misc.funcs_of_api import search_city, check_city
from utils.misc.templates_of_strings import incorrect_city
from datetime import datetime, timedelta
from handlers.default_heandlers.low_high import bots_output
from handlers.default_heandlers.bestdeal import bestdeal_output


@bot.message_handler(state=MyStates.city)
def get_city(message: Message) -> None:
    """
    Этап получения города поиска отелей.
    """
    cityname = message.text

    if cyrillic(cityname):
        bot.send_message(message.chat.id, incorrect_city)
    else:
        check = check_city(cityname)
        if check:

            s_data = search_city(cityname)
            markup = choice_city(s_data)

            bot.set_state(message.from_user.id, MyStates.city_id, message.chat.id)
            bot.send_message(message.chat.id, 'Пожалуйста, подтвердите выбор:', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, incorrect_city)


@bot.callback_query_handler(func=lambda call: True, state=MyStates.city_id)
def get_destination_id(call) -> None:
    """
    Получение gaiaID города. Запись в хранилище наименование города и его ID.
    """
    city_name = MyStates.dict_of_results[call.data]
    context_states_call(f_call=call, f_state='city_id', f_data=call.data)
    context_states_call(f_call=call, f_state='city', f_data=city_name)

    bot.set_state(call.from_user.id, MyStates.check_in, call.message.chat.id)
    my_calendar(f_call=call, f_text=start)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(), state=MyStates.check_in)
def get_date_in(call: CallbackQuery) -> None:
    """
    Получение даты начала бронирования.
    """
    result, key, step = DetailedTelegramCalendar(min_date=date_today).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите месяц и день начала бронирования отеля: {LSTEP[step]}",
                              call.message.chat.id, call.message.message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата заезда: {result}", call.message.chat.id, call.message.message_id)
        bot.set_state(call.from_user.id, MyStates.check_out, call.message.chat.id)

        context_states_call(f_call=call, f_state='check_in', f_data=result)
        my_calendar(f_call=call, f_text=stop)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(), state=MyStates.check_out)
def get_date_out(call: CallbackQuery) -> None:
    """
    Получение даты окончания бронирования.
    """

    d_start = get_state_data('check_in')
    d_buffer = datetime.strptime(str(d_start), "%Y-%m-%d")
    d_final = datetime.date(d_buffer + timedelta(days=28))

    result, key, step = DetailedTelegramCalendar(min_date=d_start,
                                                 max_date=d_final).process(call.data)
    if not result and key:
        bot.edit_message_text(f"{LSTEP[step]}", call.message.chat.id, call.message.message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата выезда: {result}", call.message.chat.id, call.message.message_id)
        bot.set_state(call.from_user.id, MyStates.hotels_count, call.message.chat.id)

        context_states_call(f_call=call, f_state='check_out', f_data=result)

        r_markup.choice_city(call)


@bot.message_handler(state=MyStates.hotels_count)
def get_count(message: Message) -> None:
    """
    Этап получения количества отелей, выводимых ботом.
    """
    try:
        if int(message.text) in r_markup.quant_city:
            r_markup.yes_no(message)
            bot.set_state(message.from_user.id, MyStates.photo_check, message.chat.id)

            context_states(message, 'hotels_count')
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, выберите от 1 до 10 вариантов.')
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите корректное значение.')


@bot.message_handler(state=MyStates.photo_check)
def get_photo(message) -> None:
    """
    Этап, на котором узнаем, желает ли пользователь полюбоваться на фото отелей.
    Если нет - завершение диалога и вывод результатов опроса.
    """
    context_states(message, 'photo_check')

    if message.text.lower() == 'да' or message.text == 'нет':
        if message.text.lower() == 'да':
            r_markup.choice_photo(message)
            bot.set_state(message.from_user.id, MyStates.photo_count)
        else:
            bot.send_message(message.chat.id, 'Отлично! Не буду показывать фото отелей.')
            bot.set_state(message.from_user.id, MyStates.end)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['photo_count'] = None

            result = answer_end_states(states_dict()) + end_text

            bot.send_message(message.chat.id, result, parse_mode='markdown', reply_markup=r_markup.one_choice())
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, ответьте "да" или "нет".')


@bot.message_handler(state=MyStates.photo_count)
def get_photo_count(message: Message) -> None:
    """
    Завершающий этап опроса пользователя.
    Вывод результатов опроса.
    """
    try:
        if int(message.text) in r_markup.quant_photo:
            bot.set_state(message.from_user.id, MyStates.end)

            context_states(message, 'photo_count')

            answer_photo = f'Количество фото по каждому отелю: {get_state_data("photo_count")}\n'
            result = (answer_end_states(states_dict()) + answer_photo + end_text)

            bot.send_message(message.chat.id, result, parse_mode='markdown', reply_markup=r_markup.one_choice())
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, выберите от 1 до 5 вариантов.')
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите корректное значение.')


@bot.message_handler(state=MyStates.end)
def final(message: Message) -> None:
    """
    Функция запускает работу API.
    """

    command = get_state_data('command')

    if message.text.lower() == 'да':
        h_sort = 'DISTANCE'
        if command == '/bestdeal':
            bot.set_state(message.from_user.id, MyStates.choice_command)
            bestdeal_output(message=message,
                            command_sort=h_sort,
                            text_to_user='Отлично! Вот, что я нашел:')

            bot.send_message(message.chat.id, 'Поиск завершен. Для просмотра доступных команд нажми /help')
        else:
            if command == '/lowprice':
                h_sort = "PRICE_LOW_TO_HIGH"
            elif command == '/highprice':
                h_sort = "PRICE"

            bot.set_state(message.from_user.id, MyStates.choice_command)
            bots_output(message=message,
                        command_sort=h_sort,
                        text_to_user='Отлично! Вот, что я нашел:')
            bot.send_message(message.chat.id, 'Поиск завершен. Для просмотра доступных команд нажми /help')
    elif message.text.lower() == 'нет':
        bot.send_message(message.chat.id,
                         'Ок, исправим. В каком городе найти отели?',
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, MyStates.city)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, ответьте "да" или "нет".', reply_markup=ReplyKeyboardRemove())
