from telebot.types import Message, InputMediaPhoto, ReplyKeyboardRemove
from loader import bot, Hotel, MyStates
from utils.misc.funcs_of_api import get_hotels, get_address, get_photo
from utils.misc.funcs_of_states import get_state_data, context_states
from utils.misc.templates_of_strings import start_lowprice, start_highprice, hotel_output, error_data
from database.funcs_of_database import rec_command, rec_hotel


def bots_output(message: Message, command_sort, text_to_user) -> None:
    """
    Основная функция для команд lowprice / highprice,
    в которой формируется вывод сообщений пользователю в соответствии с запросом.
    """
    bot.send_message(message.chat.id, text_to_user)

    user_hotels = Hotel(message.from_user.id)
    size = MyStates.dict_of_results['results_size']
    data = get_hotels(f_sort=command_sort, f_size=size)

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


@bot.message_handler(commands=['lowprice'])
def lowprice(message: Message) -> None:
    """
    Функция сортирует отели от дешевых к дорогим.
    """
    MyStates.dict_of_results.clear()
    rec_command(message, 'lowprice')
    MyStates.user_id = message.from_user.id

    bot.send_message(message.chat.id, start_lowprice)
    bot.set_state(message.from_user.id, MyStates.city, message.chat.id)
    context_states(message, 'command')


@bot.message_handler(commands=['highprice'])
def highprice(message: Message) -> None:
    """
    Функция сортирует отели от дорогих к дешевым.
    """
    MyStates.dict_of_results.clear()
    rec_command(message, 'highprice')
    MyStates.user_id = message.from_user.id

    bot.send_message(message.chat.id, start_highprice)
    bot.set_state(message.from_user.id, MyStates.city, message.chat.id)
    context_states(message, 'command')
