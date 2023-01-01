from telebot.types import Message, InputMediaPhoto, ReplyKeyboardRemove
from loader import bot, Hotel, MyStates
from utils.misc.funcs_of_api import get_hotels, get_address, get_photo
from utils.misc.funcs_of_states import get_state_data, context_states
from utils.misc.templates_of_strings import city_choice, hotel_output, error_data
from database.funcs_of_database import rec_command, rec_hotel
from keyboards.reply.r_markup import one_choice
import re


@bot.message_handler(commands=['bestdeal'])
def bestdeal(message: Message) -> None:
    """
    Команда выводит пользователю ближайшие к центру отели.
    Запрашиваем у пользователя минимальное расстояние до центра.
    """
    MyStates.dict_of_results.clear()
    rec_command(message, 'bestdeal')
    MyStates.user_id = message.from_user.id

    bot.send_message(message.chat.id, 'Сейчас я покажу отели с наиболее выгодным расположением '
                                      'относительно центра и стоимости.\n'
                                      'На каком расстоянии от центра ищем?\nМинимальное (км):')
    bot.set_state(message.from_user.id, MyStates.dist_min, message.chat.id)
    context_states(message, 'command')


@bot.message_handler(state=MyStates.dist_min)
def max_dist(message: Message) -> None:
    """
    Запрашиваем у пользователя максимальное расстояние до центра.
    """
    if not bool(re.search('[^.0-9]', message.text)):
        context_states(message, 'dist_min')
        bot.send_message(message.chat.id, 'Теперь максимально приемлемое расстояние (км):')
        bot.set_state(message.from_user.id, MyStates.dist_max, message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введи числовое значение:')


@bot.message_handler(state=MyStates.dist_max)
def max_price(message: Message) -> None:
    """
    Запрашиваем у пользователя максимальную цену за ночь.
    """
    if not bool(re.search('[^.0-9]', message.text)):
        context_states(message, 'dist_max')
        if float(get_state_data('dist_max')) > float(get_state_data('dist_min')):
            bot.send_message(message.chat.id, 'Теперь определимся с ценой.\n'
                                              'Максимально приемлемая цена за ночь ($):')
            bot.set_state(message.from_user.id, MyStates.price_max, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Максимальное расстояние должно быть больше минимального.\n'
                                              'Пожалуйста, повтори ввод.')
            bot.send_message(message.chat.id, 'Минимальное расстояние от отеля до центра города:')
            bot.set_state(message.from_user.id, MyStates.dist_min, message.chat.id)

    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введи числовое значение:')


@bot.message_handler(state=MyStates.price_max)
def min_price(message: Message) -> None:
    """
    Запрашиваем у пользователя минимальную цену за ночь.
    """
    if not bool(re.search('[^.0-9]', message.text)):
        context_states(message, 'price_max')
        bot.send_message(message.chat.id, 'Укажите также минимальную цену за ночь ($):')
        bot.set_state(message.from_user.id, MyStates.price_min, message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введи числовое значение:')


@bot.message_handler(state=MyStates.price_min)
def check_answers(message: Message) -> None:
    """
    Подтверждаем полученные данные.
    """

    if not bool(re.search(r'[^.\d]', message.text)):
        context_states(message, 'price_min')
        if float(get_state_data('price_max')) > float(get_state_data('price_min')):

            dist_min = get_state_data("dist_min")
            dist_max = get_state_data("dist_max")
            price_min = get_state_data("price_min")
            price_max = get_state_data("price_max")

            bot.send_message(message.chat.id, f'Проверим полученную информацию.\n'
                                              f'Минимальное расстояние от отеля до центра: {dist_min}\n'
                                              f'Максимальное расстояние от отеля до центра: {dist_max}\n'
                                              f'Минимальная цена за номер: {price_min}\n'
                                              f'Максимальная цена за номер: {price_max}')
            bot.send_message(message.chat.id, 'Все так?', reply_markup=one_choice())
            bot.set_state(message.from_user.id, MyStates.command, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Максимальная цена должно быть больше минимальной.\n'
                                              'Пожалуйста, повтори ввод.')
            bot.send_message(message.chat.id, 'Максимально приемлемая цена за ночь ($):')
            bot.set_state(message.from_user.id, MyStates.price_max, message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введи числовое значение:')


@bot.message_handler(state=MyStates.command)
def input_city(message: Message):
    """
    Запрашиваем искомый город.
    """
    if message.text.lower() == 'да':
        bot.send_message(message.chat.id, city_choice)
        bot.set_state(message.from_user.id, MyStates.city, message.chat.id)
    elif message.text.lower() == 'нет':
        bot.send_message(message.chat.id, 'Ок, проверим еще раз.\n'
                                          'Минимальное расстояние от отеля до центра (км):',
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, MyStates.dist_min, message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, ответь "да" или "нет".')


def bestdeal_output(message: Message, command_sort, text_to_user) -> None:
    """
    Основная функция для команды bestdeal,
    в которой формируется вывод сообщений пользователю в соответствии с запросом.
    """
    bot.send_message(message.chat.id, text_to_user)

    user_hotels = Hotel(message.from_user.id)
    data = get_hotels(f_sort=command_sort)

    size = MyStates.dict_of_results['results_size']
    h_count = 0

    for hotel in data['data']['propertySearch']['properties']:
        h_id = hotel["id"]
        h_name = hotel["name"]
        try:
            measure = hotel["destinationInfo"]["distanceFromDestination"]["unit"].lower()
        except TypeError:
            measure = error_data

        try:
            dist = hotel["destinationInfo"]["distanceFromDestination"]["value"]
        except TypeError:
            dist = error_data

        try:
            cost_day = hotel["price"]["displayMessages"][0]["lineItems"][0]["price"]["formatted"]
        except TypeError:
            cost_day = error_data

        try:
            cost_period = hotel["price"]["displayMessages"][1]["lineItems"][0]["value"]
        except TypeError:
            cost_period = error_data

        one_cost = cost_day[1:]
        if ',' in one_cost:
            one_cost = one_cost.replace(',', '')

        condition_dist = float(get_state_data('dist_min')) < float(dist) < float(get_state_data('dist_max'))
        condition_price = float(get_state_data('price_min')) < float(one_cost) < float(get_state_data('price_max'))
        check_cond = condition_dist and condition_price and (h_count < int(size))

        if check_cond:
            h_count += 1
            link_pattern = "https://www.hotels.com/h{hotelid}.hotel-information"

            h_address = get_address(hotel_id=h_id)
            h_photos = get_photo(hotel_id=h_id)

            user_hotels.hotel_id = h_id
            user_hotels.name = h_name
            user_hotels.dist_center = (measure, dist)
            user_hotels.price_day = cost_day
            user_hotels.price_total = cost_period
            user_hotels.link = link_pattern.format(hotelid=h_id)
            user_hotels.address = h_address

            user_hotels.rec_results()

            rec_hotel(message, h_name)

            bot.send_message(message.chat.id,
                             hotel_output.format(name=h_name,
                                                 address=h_address,
                                                 dist=dist,
                                                 unit=measure,
                                                 cost_one=cost_day,
                                                 full=cost_period,
                                                 link=user_hotels.link),
                             disable_web_page_preview=True,
                             parse_mode='html',
                             reply_markup=ReplyKeyboardRemove())

            if get_state_data('photo_check') == 'да':
                count = int(get_state_data('photo_count'))
                if len(h_photos) < count:
                    count = len(h_photos)

                photo_list = h_photos[:count]

                bot.send_media_group(chat_id=message.chat.id,
                                     media=[InputMediaPhoto(photo) for photo in photo_list])
        elif h_count == int(size):
            break
