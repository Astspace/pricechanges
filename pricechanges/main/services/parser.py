import requests
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import os.path
from main.services.models import Item


class ItemParserBase:
    def __init__(self, id_item: int, mode: str = 'main'):
        self.id_item = id_item
        self.item_url = None
        self.mode = mode

    def _create_item_obj(self, item_data_dict: dict) -> Item:
        item_obj = Item.model_validate(item_data_dict)
        return item_obj


class ItemParserWb(ItemParserBase):
    def parse(self) -> Item:
        params = {
            'dest': '-1257786',
            'nm': self.id_item,
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
            "price": response_json["sizes"][0]["price"]["product"],
            "item_url": f"https://www.wildberries.ru/catalog/{self.id_item}/detail.aspx",
            "marketplace": 'wb'
        }
        return self._create_item_obj(item_data_dict)


class ItemParserOzon(ItemParserBase):
    def __init_webdriver(self) -> webdriver.Chrome:
        options = Options()
        options.add_argument('--headless=new')
        driver = webdriver.Chrome(options=options)
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        return driver

    def __search_item(self, driver: webdriver.Chrome, id_item: int) -> webdriver.Chrome:
        search_field = driver.find_element(By.NAME, 'text')
        search_field.send_keys(str(id_item))
        search_field.send_keys(Keys.ENTER)
        return driver

    def __get_item_page(self, id_item: int) -> str:
        driver = self.__init_webdriver()
        driver.get('https://www.ozon.ru/')
        time.sleep(10)
        driver = self.__search_item(driver, id_item)
        self.item_url = driver.current_url
        item_page = driver.page_source
        return item_page

    def __get_pretty_soup_item_page(self, id_item: int) -> str:
        item_page = self.__get_item_page(id_item)
        soup_item_page = BeautifulSoup(item_page, 'lxml')
        pretty_soup_item_page = soup_item_page.prettify()
        return pretty_soup_item_page

    def __get_item_brand(self, item_page_soup: BeautifulSoup) -> str:
        brand = item_page_soup.find('div', {'data-widget': 'breadCrumbs'}) \
            .find_all('span')[-1] \
            .text.strip()
        return brand

    def __get_item_name(self, item_page_soup: BeautifulSoup) -> str:
        name = item_page_soup.find_all('div', {'data-widget': 'webStickyColumn'})[1] \
            .find('h1') \
            .text.strip()
        return name

    def __get_item_rating(self, item_page_soup: BeautifulSoup) -> float:
        rating = float(item_page_soup.find_all('div', {'data-widget': 'webStickyColumn'})[1] \
                       .find('svg') \
                       .find_next('div') \
                       .text.split()[0])
        return rating

    def __get_item_feedbacks(self, item_page_soup: BeautifulSoup) -> int:
        feedbacks = int(item_page_soup.find_all('div', {'data-widget': 'webStickyColumn'})[1] \
                        .find('svg') \
                        .find_next('div') \
                        .text.split()[2])
        return feedbacks

    def __get_item_volume(self, item_page_soup: BeautifulSoup) -> int:
        volume = item_page_soup.find_all('div', {'data-widget': 'webStickyColumn'})[2] \
            .find_next('span') \
            .find_next('span') \
            .text.strip()
        if len(volume.split()) > 1:
            return -1
        else:
            return int(volume)

    def __get_item_price(self, item_page_soup: BeautifulSoup) -> int:
        price = item_page_soup.find_all('div', {'data-widget': 'webStickyColumn'})[2] \
                    .find_next('div', {'data-widget': 'webPrice'}) \
                    .find_next('span', {'style': None}) \
                    .text.strip().replace(u'\u2009', '')[:-1]
        return int(price)

    def __get_item_dict(self, item_page_soup: BeautifulSoup, id_item: int) -> dict:
        item_data_dict = {
            "id": id_item,
            "item_url": self.item_url,
            "brand": self.__get_item_brand(item_page_soup),
            "name": self.__get_item_name(item_page_soup),
            "rating": self.__get_item_rating(item_page_soup),
            "feedbacks": self.__get_item_feedbacks(item_page_soup),
            "volume": self.__get_item_volume(item_page_soup),
            "price": self.__get_item_price(item_page_soup),
            "marketplace": 'ozon'
        }
        return item_data_dict

    def parse(self) -> Item:
        if self.mode == 'main':
            if not os.path.exists('main/services/page.html'):
                with open('main/services/page.html', 'w', encoding='utf-8') as page:
                    page.write(self.__get_pretty_soup_item_page(self.id_item))
            with open('main/services/page.html', 'r', encoding='utf-8') as page:
                item_page_soup = BeautifulSoup(page, 'lxml')
            item_dict = self.__get_item_dict(item_page_soup, self.id_item)
        else:
            pretty_soup_item_page = self.__get_pretty_soup_item_page(self.id_item)
            item_page_soup = BeautifulSoup(pretty_soup_item_page, 'lxml')
            item_dict = self.__get_item_dict(item_page_soup, self.id_item)
        return self._create_item_obj(item_dict)


if __name__ == "__main__":
    x = ItemParserOzon(1698963541, mode='change')
    print(x.parse())
    # y = ItemParserWb(239898267)
    # print(y.parse())
