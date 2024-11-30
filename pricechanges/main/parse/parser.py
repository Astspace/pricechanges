import requests
from models import Item
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import os.path


class ItemParserBase:
    def _create_item_obj(self, item_data_dict: dict) -> Item:
        item_obj = Item.model_validate(item_data_dict)
        return item_obj


class ItemParserWb(ItemParserBase):
    def parse(self, id_item: str) -> Item:
        params = {
            'dest': '-1257786',
            'nm': id_item,
        }
        response = requests.get('https://card.wb.ru/cards/v2/detail', params=params)
        return self.__get_item_dict(response.json()["data"]["products"][0])

    def __get_item_dict(self, response_json: dict) -> Item:
        item_data_dict = {
            "id": response_json["id"],
            "brand": response_json["brand"],
            "name": response_json["name"],
            "rating": response_json["reviewRating"],
            "feedbacks": response_json["feedbacks"],
            "volume": response_json["volume"],
            "price": response_json["sizes"][0]["price"]["product"]
        }
        return self._create_item_obj(item_data_dict)


class ItemParserOzon(ItemParserBase):
    def __init_webdriver(self) -> webdriver.Chrome:
        driver = webdriver.Chrome()
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        return driver

    def __search_item(self, driver: webdriver.Chrome, id_item: str) -> webdriver.Chrome:
        search_field = driver.find_element(By.NAME, 'text')
        search_field.send_keys(id_item)
        search_field.send_keys(Keys.ENTER)
        return driver

    def __get_item_page(self, id_item: str) -> str:
        driver = self.__init_webdriver()
        driver.get('https://www.ozon.ru/')
        time.sleep(5)
        driver = self.__search_item(driver, id_item)
        item_page = driver.page_source
        return item_page

    def __get_pretty_soup_item_page(self, id_item: str) -> str:
        item_page = self.__get_item_page(id_item)
        soup_item_page = BeautifulSoup(item_page, 'lxml')
        pretty_soup_item_page = soup_item_page.prettify()
        return pretty_soup_item_page

    def __get_item_dict(self, item_page_soup, id_item):
        item_data_dict = {
            "id": id_item,
            "brand": item_page_soup.find('div', {'data-widget': 'breadCrumbs'})
                                   .find_all('span')[-1]
                                   .text.strip(),
            "name": item_page_soup.find_all('div', {'data-widget': 'webStickyColumn'})[1]
                                  .find('h1')
                                  .text.strip(),
            "rating": float(item_page_soup.find_all('div', {'data-widget': 'webStickyColumn'})[1]
                                          .find('svg')
                                          .find_next('div')
                                          .text.strip()[:3]),
            "feedbacks": int(item_page_soup.find_all('div', {'data-widget': 'webStickyColumn'})[1]
                                           .find('svg')
                                           .find_next('div')
                                           .text.strip()[6:]
                                           .split()[0]),
            "volume": None,
            "price": None,
        }
        return item_data_dict

    def parse(self, id_item: str) -> Item:
        if not os.path.exists('page.html'):
            with open('page.html', 'w', encoding='utf-8') as page:
                page.write(self.__get_pretty_soup_item_page(id_item))
        with open('page.html', 'r', encoding='utf-8') as page:
            item_page_soup = BeautifulSoup(page, 'lxml')
        item_dict = self.__get_item_dict(item_page_soup, id_item)
        print(item_dict)

        # test = soup_item_page.find('div', {'data-widget': 'webPrice'}).find('span').text.strip()
        # print(pretty_soup_item_page.find('div', {'data-widget': 'webPrice'}))


if __name__ == "__main__":
    x = ItemParserOzon()
    x.parse("1690791181")
    # x.parse('273612215')
