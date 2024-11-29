import requests
from models import Item
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup


class ItemParser():
    def __init__(self, id_item: str):
        self.id_item = id_item

    def parse_wb(self) -> Item:
        params = {
            'dest': '-1257786',
            'nm': self.id_item,
        }
        response = requests.get('https://card.wb.ru/cards/v2/detail', params=params)
        return self.__get_item_data(response.json()["data"]["products"][0])

    def init_webdriver(self):
        driver = webdriver.Chrome()
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        return self.parse_ozon(driver)


    def parse_ozon(self, driver) -> Item:
        driver.get('https://www.ozon.ru/')
        time.sleep(10)
        search_field = driver.find_element(By.ID, 'iaa9_33 tsBody500Medium')
        search_field.send_keys('1690791181')

    def __get_item_data(self, response: dict) -> Item:
        item_data = {
            "id": self.id_item,
            "brand": response["brand"],
            "name": response["name"],
            "rating": response["reviewRating"],
            "feedbacks": response["feedbacks"],
            "volume": response["volume"],
            "price": response["sizes"][0]["price"]["product"]
        }
        return self.__create_item_obj(item_data)

    def __create_item_obj(self, item_data: dict) -> Item:
        item_obj = Item.model_validate(item_data)
        return item_obj


if __name__ == "__main__":
    x = ItemParser('256315530')
    print(x.parse_wb().name)
    x.init_webdriver()