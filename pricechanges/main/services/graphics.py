import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from io import BytesIO
import base64
from django.utils.safestring import mark_safe


def format_date_x_axis(x, pos):
    pass


def __generate_plot(price: list, dates: list):
    fig = plt.figure(figsize=(6, 6), dpi=80)
    ax = fig.add_subplot()
    fig.suptitle('История изменения цены товара')

    ax.plot(price, dates, 'go--', linewidth=2, markersize=12)

    plt.ylabel('Цена')
    plt.xlabel('Дата')
    plt.minorticks_on()
    plt.grid(which='major', color='#444', linewidth=1)

    #plt.tick_params(axis='x', labelrotation=100, labelsize=8)
    return plt


def __convert_plot_to_base64_encoded_image(ready_plt) -> str:
    buffer = BytesIO()
    ready_plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode('utf-8')
    return img_str


def generate_image_graph_price_changes(price: list, dates: list):
    ready_plt = __generate_plot(dates, price)
    img_str = __convert_plot_to_base64_encoded_image(ready_plt)
    graph = mark_safe(f'<img src="data:image/png;base64,{img_str}">')
    return graph


