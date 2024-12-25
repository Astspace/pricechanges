from main.models import Items, ItemsChanges, Profile
from main.services.graphics import GraphPriceChanges, GraphActualPrice
from main.services.models import Item
from main.services.parser import ItemParserWb as Wb
from main.services.parser import ItemParserOzon as Ozon
from django.contrib.auth import get_user_model
import time


User = get_user_model()


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
        last_price_tgbot = item.last_price
        item.last_price = parse_item.price
        item.save()
        send_price_change_message(item, parse_item, last_price_tgbot)


def send_price_change_message(item: Items, parse_item, last_price: int):
    telegram_id = check_availability_bot(item)
    if telegram_id:
        from main.management.commands.runbot import price_change_message
        price_change_message(telegram_id=telegram_id,
                             last_price=last_price,
                             actual_price=parse_item.price,
                             item=item)


def change_item_price_database() -> None:
    while True:
        items_database = Items.actual.all()
        for item in items_database:
            __update_item_for_schedule(item)
            time.sleep(5)


def get_list_item_history(item_relations: int) -> list:
    list_history = ItemsChanges.objects.filter(item_relations=item_relations)
    return list_history


def get_image_graph_price_changes(list_history: list):
    if list_history:
        graph_item_history = GraphPriceChanges(list_history).generate_image_graph_price_changes()
        return graph_item_history
    else:
        return False


def get_image_graph_actual_price(list_history: list):
    if list_history:
        graph_actual_price = GraphActualPrice(list_history).generate_image_graph_actual_prices()
        return graph_actual_price
    else:
        return False


def check_user_register_bot(telegram_id: int):
    try:
        user_id = Profile.objects.get(telegram_id=telegram_id).user_relations_id
    except Profile.DoesNotExist:
        return False
    else:
        user = User.objects.get(id=user_id)
        return user


def search_user_by_username(username: str):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    else:
        return user


def binding_site_user_tgbot(message):
    user = search_user_by_username(message.from_user.text)
    if user:
        create_user_tgbot(user_id=user.id, telegram_id=message.from_user.id)


def create_user_tgbot(user_id: int, telegram_id: int):
    Profile.objects.create(telegram_id=telegram_id, user_relations_id=user_id)


def check_availability_bot(item: Items):
    user_id = item.owner.id
    try:
        profile = Profile.objects.get(user_relations_id=user_id)
    except User.DoesNotExist:
        return False
    else:
        return profile.telegram_id


def get_item_list_tgbot(telegram_id: int):
    user_id = Profile.objects.get(telegram_id=telegram_id).user_relations_id
    items_list = Items.actual.filter(owner=user_id)
    return items_list