from main.models import Items, ItemsChanges
from main.services.models import Item
from main.services.parser import ItemParserWb as Wb
from main.services.parser import ItemParserOzon as Ozon


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


def change_item_price_database() -> None:
    while True:
        items_database = Items.actual.all()
        for item in items_database:
            parse_item = __get_parse_item(item)
            if not __check_price_changes(item.last_price, parse_item.price):
                __update_item_price_database(item_db=item, parse_item=parse_item)
                item.last_price = parse_item.price
                item.save()
