from django.core.management.base import BaseCommand
from main.services.processors import change_item_price_database


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        change_item_price_database()
