from datetime import datetime
from django.db.models import QuerySet
from loguru import logger
from telebot.types import Message
from main.models import Items, ItemsChanges, Profile
from main.services.graphics import GraphPriceChanges, GraphActualPrice
from main.services.models import Item
from main.services.parser import ItemParserWb as Wb
from main.services.parser import ItemParserOzon as Ozon
from django.contrib.auth import get_user_model
import time
from typing import Literal, Optional

User = get_user_model()


@logger.catch
def preparation_data_for_create_item(data_for_create_item: Items) -> str | Items:
    marketplace = data_for_create_item.mtplace.name
    id_item = data_for_create_item.id_item
    if marketplace == 'Wb':
        item_obj = Wb(id_item=id_item).parse()
    else:
        item_obj = Ozon(id_item=id_item).parse()
    if isinstance(item_obj, str):
        return item_obj
    return __get_refresh_data_for_create_item(data_for_create_item, item_obj)


def __get_refresh_data_for_create_item(data_for_create_item: Items, item_obj: Item) -> str | Items:
    try:
        data_for_create_item.item_url = item_obj.item_url
        data_for_create_item.name = item_obj.name
        data_for_create_item.rating = item_obj.rating
        data_for_create_item.feedbacks = item_obj.feedbacks
        data_for_create_item.volume = item_obj.volume
        data_for_create_item.brand = item_obj.brand
        data_for_create_item.price = item_obj.price
        data_for_create_item.last_price = item_obj.price
        return data_for_create_item
    except Exception:
        msg_err = 'Ошибка подготовки данных для добавления нового товара в БД'
        logger.exception(msg_err)
        return msg_err


@logger.catch
def __check_price_changes(item_price_database: int, item_price_parse: int) -> bool:
    return False if item_price_database == item_price_parse else True


def __update_item_price_database(item_db: Items, parse_item: Item) -> Optional[str]:
    try:
        ItemsChanges.objects.create(item_relations=item_db,
                                    name=parse_item.name,
                                    feedbacks=parse_item.feedbacks,
                                    price=parse_item.price,
                                    rating=parse_item.rating,
                                    volume=parse_item.volume)
    except Exception:
        err_msg = 'Не удалось создать новую запись в истории изменения товара (новый товар)'
        logger.exception(err_msg)
        return err_msg


def history_for_created_item(created_item: Items) -> Optional[str]:
    name = created_item.name_for_user if created_item.name_for_user else created_item.name
    try:
        ItemsChanges.objects.create(item_relations=created_item,
                                    name=name,
                                    feedbacks=created_item.feedbacks,
                                    price=created_item.price,
                                    rating=created_item.rating,
                                    volume=created_item.volume)
    except Exception:
        err_msg = 'Не удалось создать новую запись в истории изменения товара (существующий товар)'
        logger.exception(err_msg)
        return err_msg


@logger.catch
def __get_parse_item(item: Items) -> Item | str:
    if item.mtplace.name == 'Wb':
        parse_item: Item = Wb(id_item=item.id_item).parse()
    else:
        parse_item: Item = Ozon(id_item=item.id_item).parse()
    return parse_item


def __update_item_for_schedule(item: Items) -> Item | str:
    parse_item = __get_parse_item(item)
    if isinstance(parse_item, str):
        return parse_item
    item_name = item.name_for_user if item.name_for_user else item.name
    if __check_price_changes(item.last_price, parse_item.price):
        res_update = __update_item_price_database(item_db=item, parse_item=parse_item)
        if res_update:
            return res_update
        last_price_tgbot = item.last_price
        item.last_price = parse_item.price
        if parse_item.name == 'Наименование не определено' and \
                -1 in (parse_item.feedbacks, parse_item.price, parse_item.rating, parse_item.volume):
            item.out = True
            msg = send_price_change_message(item=item, parse_item=parse_item, last_price=last_price_tgbot, item_out=True)
            if msg:
                return msg
            create_change_item_logs(mode='out', item_name=item_name, actual_price=last_price_tgbot)
        else:
            item.out = False
            msg = send_price_change_message(item=item, parse_item=parse_item, last_price=last_price_tgbot)
            if msg:
                return msg
            create_change_item_logs(mode='change', item_name=item_name, actual_price=item.last_price,
                                    last_price=last_price_tgbot)
        try:
            item.save()
        except Exception:
            err_msg = 'Не удалось изменить последнню цену товара (сохранить данные)'
            logger.exception(err_msg)
            return err_msg
    else:
        create_change_item_logs(mode='no_change', item_name=item_name, actual_price=item.last_price)
    return parse_item


def send_price_change_message(item: Items, parse_item, last_price: int, item_out: bool = False) -> Optional[str]:
    telegram_id = check_availability_bot(item)
    if isinstance(telegram_id, str):
        return telegram_id
    if item_out:
        from main.management.commands.runbot import price_change_message_item_out
        msg = price_change_message_item_out(telegram_id=telegram_id,
                                            last_price=last_price,
                                            item=item)
        if msg:
            logger.exception(msg)
            return msg
    else:
        from main.management.commands.runbot import price_change_message
        msg = price_change_message(telegram_id=telegram_id,
                                   last_price=last_price,
                                   actual_price=parse_item.price,
                                   item=item)
        if msg:
            logger.exception(msg)
            return msg


def send_add_item_message(created_item: Items) -> Optional[str]:
    telegram_id = check_availability_bot(created_item)
    if isinstance(telegram_id, str):
        return telegram_id
    from main.management.commands.runbot import add_item_message
    return add_item_message(telegram_id, created_item)


def change_item_price_database() -> Optional[str]:
    while True:
        try:
            items_database = Items.actual.all()
        except Exception:
            err_msg = 'Ошибка при получения списка товаров для дальнейшего сканирования'
            logger.exception(err_msg)
            return err_msg
        for item in items_database:
            res_update_item = __update_item_for_schedule(item)
            if isinstance(res_update_item, str):
                logger.exception(res_update_item)
            time.sleep(5)


def get_list_item_history(item_relations: int) -> QuerySet | str:
    try:
        list_history = ItemsChanges.objects.filter(item_relations=item_relations)
        return list_history
    except Exception:
        err_msg = f'Ошибка при попытке получить историю изменения товара (id = {item_relations})'
        logger.exception(err_msg)
        return err_msg


def get_image_graph_price_changes(list_history: QuerySet) -> str:
    if not isinstance(list_history, QuerySet):
        err_msg = 'Ошибка получения данных об истории изменения товара'
        logger.exception(err_msg)
        return err_msg
    graph_item_history = GraphPriceChanges(list_history).generate_image_graph_price_changes()
    return graph_item_history


def get_image_graph_actual_price(list_history: list) -> str:
    if isinstance(list_history, str):
        logger.exception(list_history)
        return list_history
    graph_actual_price = GraphActualPrice(list_history).generate_image_graph_actual_prices()
    return graph_actual_price


def check_user_register_bot(telegram_id: int) -> Optional[str]:
    try:
        user_id = Profile.objects.get(telegram_id=telegram_id).user_relations_id
        user = User.objects.get(id=user_id)
        return user
    except Exception:
        logger.exception('Возникла ошибка при попытке определить профиль пользователя по tg-аккаунту.')


def search_user_by_username(username: str) -> QuerySet | bool:
    try:
        user = User.objects.get(username=username)
        return user
    except Exception:
        err_msg = 'Ошибка при попытке получить профиль пользователя.'
        logger.exception(err_msg)
        return err_msg


def binding_site_user_tgbot(message: Message) -> Optional[str]:
    user = search_user_by_username(message.from_user.text)
    if isinstance(user, str):
        return user
    create_tg_user = create_user_tgbot(user_id=user.id, telegram_id=message.from_user.id)
    if isinstance(create_tg_user, str):
        return create_tg_user


def create_user_tgbot(user_id: int, telegram_id: int) -> Optional[str]:
    try:
        Profile.objects.create(telegram_id=telegram_id, user_relations_id=user_id)
    except Exception:
        err_msg = 'Ошибка при попытке создать профиль пользователя (для привязки tg)'
        logger.exception(err_msg)
        return err_msg


def check_availability_bot(item: Items) -> int | str:
    user_id = item.owner.id
    try:
        profile = Profile.objects.get(user_relations_id=user_id)
        return profile.telegram_id
    except Exception:
        err_msg = 'Ошибка при попытке получить id tg-профиля'
        logger.exception(err_msg)
        return err_msg


def get_item_list_tgbot(telegram_id: int) -> QuerySet | str:
    try:
        user_id = Profile.objects.get(telegram_id=telegram_id).user_relations_id
        items_list = Items.actual.filter(owner=user_id)
        return items_list
    except Exception:
        err_msg = 'Не удалось получить список товаров пользователя по данным tg.'
        logger.exception(err_msg)
        return err_msg


def get_image_graph_actual_price_tgbot(mktplace_item_id: int, telegram_id: int) -> str | list[str]:
    list_history = get_list_history_item_tgbot(mktplace_item_id, telegram_id)
    if isinstance(list_history, str):
        return [list_history]
    user_id = Profile.objects.get(telegram_id=telegram_id).user_relations_id
    user_name = User.objects.get(id=user_id).username
    graph_actual_price = GraphActualPrice(list_history).save_image_graph_actual_prices_tgbot(user_name=user_name)
    return graph_actual_price


def get_list_history_item_tgbot(mktplace_item_id: int, telegram_id) -> QuerySet | str:
    try:
        user_id = Profile.objects.get(telegram_id=telegram_id).user_relations_id
        item = Items.actual.get(id_item=mktplace_item_id, owner=user_id)
    except Exception:
        err_msg = 'Не удалось получить данные о товаре пользователя.'
        logger.exception(err_msg)
        return err_msg
    item_history = get_list_item_history(item_relations=item.id)
    return item_history


def get_item_data(item_id: int) -> Items | str:
    try:
        item: Items = Items.actual.get(id=item_id)
        return item
    except Exception:
        msg_err = 'Ошибка при поиске товара по его id'
        return msg_err


@logger.catch
def create_change_item_logs(mode: Literal['change', 'no_change', 'out'],
                            item_name: str,
                            actual_price: int,
                            last_price: int = None) -> None:
    log_text = f'{datetime.now().replace(microsecond=0)} '
    if mode == 'change':
        log_text += f'ЦЕНА НА ТОВАР ИЗМЕНИЛАСЬ! Наименование: {item_name}. ' \
                    f'Старая цена: {last_price}, ' \
                    f'новая цена: {actual_price}\n'
    elif mode == 'no_change':
        log_text += f'Цена на товар не изменилась! Наименование: {item_name}. ' \
                    f'Цена: {actual_price}\n'
    elif mode == 'out':
        log_text += f'ТОВАР ЗАКОНЧИЛСЯ! Наименование: {item_name}. ' \
                    f'Цена: {actual_price}\n'
    with open('main/logs/change_item.txt', 'a') as file:
        file.write(log_text)
