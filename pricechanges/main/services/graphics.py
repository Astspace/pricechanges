import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
from django.utils.safestring import mark_safe
from django.db.models import QuerySet
from loguru import logger


class GraphBase:
    @logger.catch
    def _get_time_creates_list(self) -> list:
        list_time_creates = [i.time_create.date() for i in self.item_history]
        return list_time_creates

    @logger.catch
    def _get_prices_list(self) -> list:
        list_prices = [i.price for i in self.item_history]
        return list_prices

    @classmethod
    def _convert_plot_to_base64_encoded_image(cls, ready_plt) -> list[str] | str:
        try:
            buffer = BytesIO()
            ready_plt.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)
            img_str = base64.b64encode(buffer.read()).decode('utf-8')
            return img_str
        except Exception:
            err_msg = 'Ошибка преобразования графика в изображение'
            logger.exception(err_msg)
            return [err_msg]

    def generate_image_graph(self, ready_plt) -> list[str] | str:
        img_str = self._convert_plot_to_base64_encoded_image(ready_plt)
        if isinstance(img_str, list):
            return img_str
        graph = mark_safe(f'<img src="data:image/png;base64,{img_str}">')
        return graph


class GraphPriceChanges(GraphBase):
    def __init__(self, item_history: QuerySet):
        self.item_history = item_history

    def __generate_plot_graph_price_changes(self) -> plt | str:
        try:
            fig = plt.figure(figsize=(8, 4), dpi=80)
            fig.suptitle('История изменения цены товара')
            list_prices = self._get_prices_list()
            list_time_creates = self._get_time_creates_list()
            plt.plot(list_time_creates, list_prices, 'go--', linewidth=2, markersize=12)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
            return self.__display_graph_price_changes(plt)
        except Exception:
            err_msg = 'Ошибка формирования графика изменения цены товара'
            logger.exception(err_msg)
            return err_msg

    @logger.catch
    def __display_graph_price_changes(self, plt) -> plt:
        plt.ylabel('Цена')
        plt.xlabel('Дата')
        plt.minorticks_on()
        plt.grid(which='major', color='#444', linewidth=1)
        plt.xticks(rotation=45)
        return plt

    def generate_image_graph_price_changes(self) -> list[str] | str:
        plot_graph_price_changes = self.__generate_plot_graph_price_changes()
        if isinstance(plot_graph_price_changes, str):
            return [plot_graph_price_changes]
        image_graph = self.generate_image_graph(plot_graph_price_changes)
        return image_graph


class GraphActualPrice(GraphBase):
    def __init__(self, item_history: QuerySet):
        self.item_history = item_history.filter(price__gt=-1)
        self.actual_price = item_history.last().price
        self.min_price = self.item_history.order_by('price').first().price
        self.max_price = self.item_history.order_by('price').last().price

    def __generate_plot_graph_actual_price(self) -> plt | str:
        try:
            fig = plt.figure(figsize=(8, 4), dpi=80)
            fig.suptitle('Сравнение минимальной, текущей и максимальной цен товара')
            category = ['Min', 'Текущая цена', 'Max']
            values = [self.min_price, self.actual_price, self.max_price]
            colors = ['#00BFFF', '#7FFFD4', '#CD5C5C']
            plt.bar(category, values, color=colors, width=1)
            return self.__display_graph_actual_price(plt)
        except Exception:
            err_msg = 'Ошибка формирования графика анализа актуальной цены товара'
            logger.exception(err_msg)
            return err_msg

    @logger.catch
    def __display_graph_actual_price(self, plt) -> plt:
        plt.axhline(y=self.max_price, color='red', linestyle='dashed', label='Максимальное значение')
        plt.axhline(y=self.min_price, color='blue', linestyle='dashed', label='Минимальное значение')
        plt.text(0, self.min_price, f'Min: {self.min_price}',
                 ha='center', va='bottom', color='blue', fontsize=10)
        plt.text(1, self.actual_price, f'{self.actual_price if self.actual_price != -1 else 'товар закончился'}',
                 ha='center', va='bottom', color='black', fontsize=10)
        plt.text(2, self.max_price, f'Max: {self.max_price}',
                 ha='center', va='bottom', color='red', fontsize=10)
        plt.ylabel('Цена')
        return plt

    def generate_image_graph_actual_prices(self) -> list[str] | str:
        plot_graph_actual_prices = self.__generate_plot_graph_actual_price()
        if isinstance(plot_graph_actual_prices, str):
            return plot_graph_actual_prices
        image_graph = self.generate_image_graph(plot_graph_actual_prices)
        return image_graph

    def generate_image_graph_actual_prices_tgbot(self) -> list[str] | str:
        plot_graph_actual_prices = self.__generate_plot_graph_actual_price()
        if isinstance(plot_graph_actual_prices, str):
            return plot_graph_actual_prices
        image_graph = self._convert_plot_to_base64_encoded_image(plot_graph_actual_prices)
        return image_graph

    def save_image_graph_actual_prices_tgbot(self, user_name: str) -> list[str] | str:
        image_graph = self.generate_image_graph_actual_prices_tgbot()
        if isinstance(image_graph, list):
            return image_graph
        path = f'main/services/image_{user_name}.jpg'
        image_data = base64.b64decode(image_graph)
        with open(path, 'wb') as image:
            image.write(image_data)
        return path
