from main.models import Items, ItemsChanges
from main.services.graphics import generate_image_graph_price_changes
from main.services.models import Item
from main.services.parser import ItemParserWb as Wb
from main.services.parser import ItemParserOzon as Ozon
import time
from datetime import datetime


def preparation_data_for_create_item(data_for_create_item):
    marketplace = data_for_create_item.mtplace.name
    id_item = data_for_create_item.id_item
    if marketplace == 'Wb':
        item_obj = Wb(id_item).parse()
    else:
        item_obj = Ozon(id_item=id_item, mode='for_changes').parse()
    return __refresh_data_for_create_item(data_for_create_item, item_obj)


def __refresh_data_for_create_item(data_for_create_item, item_obj: Item):
    data_for_create_item.item_url = item_obj.item_url
    data_for_create_item.name = item_obj.name
    data_for_create_item.rating = item_obj.rating
    data_for_create_item.feedbacks = item_obj.feedbacks
    data_for_create_item.volume = item_obj.volume
    data_for_create_item.brand = item_obj.brand
    data_for_create_item.price = item_obj.price
    data_for_create_item.last_price = item_obj.price
    return data_for_create_item


def __check_price_changes(item_price_database: int, item_price_parse: int):
    if item_price_database == item_price_parse:
        return True
    else:
        return False


def __update_item_price_database(item_db: Items, parse_item: Item) -> None:
    ItemsChanges.objects.create(item_relations=item_db,
                                name=parse_item.name,
                                feedbacks=parse_item.feedbacks,
                                price=parse_item.price,
                                rating=parse_item.rating,
                                volume=parse_item.volume)


def __get_parse_item(item: Items):
    if item.mtplace.name == 'Wb':
        parse_item: Item = Wb(id_item=item.id_item).parse()
    else:
        parse_item: Item = Ozon(id_item=item.id_item, mode='for_changes').parse()
    return parse_item


def __update_item_for_schedule(item: Items):
    parse_item = __get_parse_item(item)
    if not __check_price_changes(item.last_price, parse_item.price):
        __update_item_price_database(item_db=item, parse_item=parse_item)
        item.last_price = parse_item.price
        item.save()


def change_item_price_database() -> None:
    while True:
        items_database = Items.actual.all()
        for item in items_database:
            __update_item_for_schedule(item)
            time.sleep(10)


def get_list_item_history(item_relations: int) -> list:
    list_history = ItemsChanges.objects.filter(item_relations=item_relations)
    return list_history


def __get_data_for_graph_price_changes(list_history: list):
    list_prices = [i.price for i in list_history]
    list_time_creates = [i.time_create.date() for i in list_history]
    return list_prices, list_time_creates


def get_image_graph_price_changes(list_history: list):
    list_prices, list_time_creates = __get_data_for_graph_price_changes(list_history)
    graph_item_history = generate_image_graph_price_changes(price=list_prices, dates=list_time_creates)
    return graph_item_history
