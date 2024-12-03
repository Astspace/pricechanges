from .parser import ItemParserWb as Wb
from .parser import ItemParserOzon as Ozon
from .models import Item


def preparation_data_for_create_item(data_for_create_item):
    marketplace = data_for_create_item.mtplace.name
    id_item = data_for_create_item.id_item
    if marketplace == 'wb':
        item_obj = Wb(id_item).parse()
    else:
        item_obj = Ozon(id_item).parse()
    return __refresh_data_for_create_item(data_for_create_item, item_obj)


def __refresh_data_for_create_item(data_for_create_item, item_obj: Item):
    data_for_create_item.name = item_obj.name
    data_for_create_item.rating = item_obj.rating
    data_for_create_item.feedbacks = item_obj.feedbacks
    data_for_create_item.volume = item_obj.volume
    data_for_create_item.brand = item_obj.brand
    data_for_create_item.price = item_obj.price
    return data_for_create_item

