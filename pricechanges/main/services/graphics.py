import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
from io import BytesIO
import base64
from django.utils.safestring import mark_safe


class GraphBase():
    def __convert_plot_to_base64_encoded_image(self, ready_plt) -> str:
        buffer = BytesIO()
        ready_plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode('utf-8')
        return img_str

    def generate_image_graph(self, ready_plt):
        img_str = self.__convert_plot_to_base64_encoded_image(ready_plt)
        graph = mark_safe(f'<img src="data:image/png;base64,{img_str}">')
        return graph


class GraphPriceChanges(GraphBase):
    def __init__(self, price, dates):
        self.price = price
        self.dates = dates

    def __generate_plot_graph_price_changes(self):
        fig = plt.figure(figsize=(8, 4), dpi=80)
        fig.suptitle('История изменения цены товара')
        plt.plot(self.dates, self.price, 'go--', linewidth=2, markersize=12)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
        return self.__display_graph_price_changes(plt)

    def __display_graph_price_changes(self, plt):
        plt.ylabel('Цена')
        plt.xlabel('Дата')
        plt.minorticks_on()
        plt.grid(which='major', color='#444', linewidth=1)
        plt.xticks(rotation=45)
        return plt

    def generate_image_graph_price_changes(self):
        plot_graph_price_changes = self.__generate_plot_graph_price_changes()
        image_graph = self.generate_image_graph(plot_graph_price_changes)
        return image_graph


class GraphActualPrice(GraphBase):
    def __init__(self, prices: dict):
        pass