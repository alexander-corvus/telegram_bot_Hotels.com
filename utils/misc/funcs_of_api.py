from config_data.config import RAPID_API_KEY
from loader import MyStates
import requests
import json


def request_to_api(f_url, f_headers, f_querystring):
    try:
        f_response = requests.get(f_url, headers=f_headers, params=f_querystring, timeout=10)
        if f_response.status_code == requests.codes.ok:
            return f_response
    except Exception as ex:
        print(f'\nПри обработке запроса к URL:\n{f_url}\nВозникло исключение:\n{ex}')


def request_post(f_url, f_json, f_headers):
    try:
        f_response = requests.post(url=f_url, json=f_json, headers=f_headers, timeout=10)
        if f_response.status_code == requests.codes.ok:
            return f_response
    except Exception as ex:
        print(f'\nПри обработке запроса к URL:\n{f_url}\nВозникло исключение:\n{ex}')


def check_city(text) -> bool:
    """
    Проверка наличия вариантов запрашиваемого города в базе Hotels.com
    """
    data = search_city(text)

    results = [elem['type'] for elem in data['sr']]

    if 'CITY' in results:
        return True
    else:
        return False


def search_city(text) -> dict:
    """
    Поиск города по наименованию через API Hotels.com
    """
    se_url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    se_querystring = {"q": f"{text}", "locale": "eu", "langid": "1033", "siteid": "300000001"}
    se_headers = {"X-RapidAPI-Key": RAPID_API_KEY,
                  "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}

    se_response = request_to_api(f_url=se_url, f_headers=se_headers, f_querystring=se_querystring)
    try:
        se_data = json.loads(se_response.text)
        return se_data
    except AttributeError as ex:
        print(f'Функция: search_city\nИсключение: {ex}\n')
        print('Ответ сервера:', se_response)


def get_hotels(f_sort: str, f_size='200') -> dict:
    """
    Поиск основных данных по конкретно взятому отелю через API Hotels.com.
    :return: словарь с данными
    """
    into = MyStates.dict_of_results['checkin_tpl']
    out = MyStates.dict_of_results['checkout_tpl']
    # size = MyStates.dict_of_results['results_size']

    pr_url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    pr_payload = {
        "currency": "USD",

        "locale": "eu",
        "siteId": 300000001,
        "destination": {"regionId": f"{MyStates.dict_of_results['city_id']}"},
        "checkInDate": {"day": into[2],
                        "month": into[1],
                        "year": into[0]},
        "checkOutDate": {"day": out[2],
                         "month": out[1],
                         "year": out[0]},
        "rooms": [{"adults": 1}],
        "resultsStartingIndex": 0,
        "resultsSize": f_size,
        "sort": f_sort
    }

    pr_headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    pr_response = request_post(f_url=pr_url, f_json=pr_payload, f_headers=pr_headers)
    pr_data = json.loads(pr_response.text)

    return pr_data


def get_detail(hotel_id) -> dict:
    """
    Функция получает детализированную информацию по отелю через API Hotels.com
    :param hotel_id: ID отеля, полученное функцией get_hotels
    :return: словарь с данными отеля
    """

    dt_url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    dt_payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": f"{hotel_id}"
    }

    dt_headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    dt_response = requests.post(url=dt_url, json=dt_payload, headers=dt_headers)
    try:
        dt_data = json.loads(dt_response.text)
        return dt_data
    except AttributeError as ex:
        print(f'Функция: get_detail\nИсключение: {ex}')
        print('Ответ сервера:', dt_response)


def get_address(hotel_id) -> str:
    """
    Получаем адрес отеля по ID отеля через API Hotels.com
    :param hotel_id: ID отеля, полученное функцией get_hotels
    :return: строка с адресом отеля
    """

    total_data = get_detail(hotel_id)
    try:
        address = total_data["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"]
        return address
    except TypeError as ex:
        print(f'Функция: get_detail\nИсключение: {ex}')
        print('Ответ сервера', total_data)


def get_photo(hotel_id) -> list:
    """
    Получаем фото отеля по ID отеля через API Hotels.com
    :param hotel_id: ID отеля, полученное функцией get_hotels
    :return: список ссылок на фото отеля
    """

    total_data = get_detail(hotel_id)
    try:
        list_objects = total_data["data"]["propertyInfo"]["propertyGallery"]["images"]
        list_photo = [elem["image"]["url"] for elem in list_objects]
        return list_photo
    except TypeError as ex:
        print(f'Функция: get_photo\nИсключение: {ex}')
        print('Ответ сервера', total_data)


