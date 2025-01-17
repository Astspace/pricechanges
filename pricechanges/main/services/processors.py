from django.db.models import QuerySet
from telebot.types import Message
from main.models import Items, ItemsChanges, Profile
from main.services.graphics import GraphPriceChanges, GraphActualPrice
from main.services.models import Item
from main.services.parser import ItemParserWb as Wb
from main.services.parser import ItemParserOzon as Ozon
from django.contrib.auth import get_user_model
import time


User = get_user_model()


def preparation_data_for_create_item(data_for_create_item: Items) -> str | Items:
    marketplace = data_for_create_item.mtplace.name
    id_item = data_for_create_item.id_item
    if marketplace == 'Wb':
        item_obj = Wb(id_item).parse()
    else:
        item_obj = Ozon(id_item=id_item, mode='for_changes').parse()
    if isinstance(item_obj, str):
        return item_obj
    else:
        return __refresh_data_for_create_item(data_for_create_item, item_obj)


def __refresh_data_for_create_item(data_for_create_item: Items, item_obj: Item) -> Items:
    data_for_create_item.item_url = item_obj.item_url
    data_for_create_item.name = item_obj.name
    data_for_create_item.rating = item_obj.rating
    data_for_create_item.feedbacks = item_obj.feedbacks
    data_for_create_item.volume = item_obj.volume
    data_for_create_item.brand = item_obj.brand
    data_for_create_item.price = item_obj.price
    data_for_create_item.last_price = item_obj.price
    return data_for_create_item


def __check_price_changes(item_price_database: int, item_price_parse: int) -> bool:
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


def history_for_created_item(created_item: Items) -> None:
    try:
        name = created_item.name_for_user if created_item.name_for_user else created_item.name
        ItemsChanges.objects.create(item_relations=created_item,
                                    name=name,
                                    feedbacks=created_item.feedbacks,
                                    price=created_item.price,
                                    rating=created_item.rating,
                                    volume=created_item.volume)
    except Exception as e:
        print('Не удалось создать историческую запись для вновь добавленного товара!')
        print(e)


def __get_parse_item(item: Items) -> Item | str:
    if item.mtplace.name == 'Wb':
        parse_item: Item = Wb(id_item=item.id_item).parse()
    else:
        parse_item: Item = Ozon(id_item=item.id_item, mode='for_changes').parse()
    return parse_item


def __update_item_for_schedule(item: Items) -> Item | str:
    parse_item = __get_parse_item(item)
    if isinstance(parse_item, str):
        return parse_item
    if not __check_price_changes(item.last_price, parse_item.price):
        __update_item_price_database(item_db=item, parse_item=parse_item)
        last_price_tgbot = item.last_price
        item.last_price = parse_item.price
        if parse_item.name == 'Наименование не определено' and -1 in (parse_item.feedbacks, parse_item.price, parse_item.rating, parse_item.volume):
            item.out = True
            send_price_change_message(item=item, parse_item=parse_item, last_price=last_price_tgbot, item_out=True)
        else:
            item.out = False
            send_price_change_message(item=item, parse_item=parse_item, last_price=last_price_tgbot)
        item.save()
    return parse_item


def send_price_change_message(item: Items, parse_item, last_price: int, item_out: bool = False) -> None:
    telegram_id = check_availability_bot(item)
    if telegram_id:
        if item_out:
            from main.management.commands.runbot import price_change_message_item_out
            try:
                price_change_message_item_out(telegram_id=telegram_id,
                                              last_price=last_price,
                                              item=item)
            except Exception:
                print('Не удалось отправить сообщение через телеграм-бота о том, что товар закончился.')
        else:
            from main.management.commands.runbot import price_change_message
            try:
                price_change_message(telegram_id=telegram_id,
                                     last_price=last_price,
                                     actual_price=parse_item.price,
                                     item=item)
            except Exception:
                print('Не удалось отправить сообщение через телеграм-бота об изменении цены товара.')
    else:
        print('Не удалось определить телеграм-профиль пользователя при отправке сообщения об изменении цены товара.')


def send_add_item_message(created_item: Items):
    telegram_id = check_availability_bot(created_item)
    if telegram_id:
        from main.management.commands.runbot import add_item_message
        try:
            add_item_message(telegram_id, created_item)
        except Exception as e:
            print(e, 'Не удалось отправить сообщение через телеграм-бота о добавлении нового товара.')
    else:
        print('Не удалось определить телеграм-профиль пользователя при отправке сообщения о добавлении нового товара.')


def change_item_price_database() -> None:
    while True:
        items_database = Items.actual.all()
        for item in items_database:
            res_update_item = __update_item_for_schedule(item)
            if isinstance(res_update_item, str):
                print(res_update_item)
            time.sleep(5)


def get_list_item_history(item_relations: int) -> list:
    list_history = ItemsChanges.objects.filter(item_relations=item_relations)
    return list_history


def get_image_graph_price_changes(list_history: list) -> str | bool:
    if list_history:
        graph_item_history = GraphPriceChanges(list_history).generate_image_graph_price_changes()
        return graph_item_history
    else:
        return False


def get_image_graph_actual_price(list_history: list) -> str | bool:
    if list_history:
        graph_actual_price = GraphActualPrice(list_history).generate_image_graph_actual_prices()
        return graph_actual_price
    else:
        return False


def check_user_register_bot(telegram_id: int) -> QuerySet | bool:
    try:
        user_id = Profile.objects.get(telegram_id=telegram_id).user_relations_id
    except Profile.DoesNotExist:
        return False
    else:
        user = User.objects.get(id=user_id)
        return user


def search_user_by_username(username: str) -> QuerySet | bool:
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    else:
        return user


def binding_site_user_tgbot(message: Message) -> None:
    user = search_user_by_username(message.from_user.text)
    if user:
        create_user_tgbot(user_id=user.id, telegram_id=message.from_user.id)


def create_user_tgbot(user_id: int, telegram_id: int) -> None:
    Profile.objects.create(telegram_id=telegram_id, user_relations_id=user_id)


def check_availability_bot(item: Items) -> int | bool:
    user_id = item.owner.id
    try:
        profile = Profile.objects.get(user_relations_id=user_id)
    except Profile.DoesNotExist:
        return False
    else:
        return profile.telegram_id


def get_item_list_tgbot(telegram_id: int) -> QuerySet | str:
    try:
        user_id = Profile.objects.get(telegram_id=telegram_id).user_relations_id
    except Profile.DoesNotExist:
        return 'Tg-профиль не найден!'
    items_list = Items.actual.filter(owner=user_id)
    if items_list:
        return items_list
    else:
        return 'Отслеживаемые товары не найдены!'


def get_image_graph_actual_price_tgbot(mktplace_item_id: int, telegram_id: int) -> str | bool:
    list_history = get_list_history_item_tgbot(mktplace_item_id, telegram_id)
    if list_history:
        user_id = Profile.objects.get(telegram_id=telegram_id).user_relations_id
        user_name = User.objects.get(id=user_id).username
        graph_actual_price = GraphActualPrice(list_history).save_image_graph_actual_prices_tgbot(user_name=user_name)
        return graph_actual_price
    else:
        return False


def get_list_history_item_tgbot(mktplace_item_id: int, telegram_id) -> list | bool:
    user_id = Profile.objects.get(telegram_id=telegram_id).user_relations_id
    try:
        item = Items.actual.get(id_item=mktplace_item_id, owner=user_id)
    except Items.DoesNotExist:
        return False
    item_history = get_list_item_history(item_relations=item.id)
    return item_history


def get_item_data(item_id: int) -> Items | str:
    try:
        item: Items = Items.actual.get(id=item_id)
    except Items.DoesNotExist:
        return 'Не удалось найти товар!'
    return item
