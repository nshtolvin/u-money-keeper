# -*- coding: utf-8 -*-
#

# region Import
from kivy.uix.screenmanager import Screen

import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
# endregion Import


class BarChart(Screen):
    def on_enter(self):
        pass

    def update_chart(self, chart_data):
        """
        Метод обновления круговой диаграммы BarChart
        @param chart_data: словарь с данные для построения диаграммы. Ключи: data - список с суммами расходов
        по катеогриям; categories_names - наименование категорий расходов; colors - список цветов, которыми будут
        обозначены категории расходов на диаграмме
        @return: None
        """
        # параметры оформления диаграммы
        figure, axes = plt.subplots()
        # задаем цвет и прозрачность фона диаграммы, а также внутренней области диаграммы
        figure.patch.set_facecolor('whitesmoke')
        figure.patch.set_alpha(0.8)
        axes.patch.set_facecolor('whitesmoke')
        axes.patch.set_alpha(0.8)

        # удаляем левую и нижнюю границу области диаграммы
        # axes.spines['left'].set_visible(False)
        axes.spines['top'].set_visible(False)
        axes.spines['right'].set_visible(False)
        # axes.spines['bottom'].set_visible(False)

        # добавляем подписи к осям диаграммы (поворот меток, выравнивание, размер шрифта)
        plt.yticks(rotation=45, horizontalalignment='right', fontsize=7)
        plt.xticks(horizontalalignment='center', fontsize=7)

        # добавляем столбчатаю диаграмму
        # bottom_sum - накопительный массив, в котором содержится начальная высота, с которой нчинается
        # следующая часть накопительного столбца
        bottom_sum = chart_data["data"][0].copy()
        plt.bar(chart_data["dates"], chart_data["data"][0], color=chart_data["colors"][0], width=0.4)
        for ind in range(1, len(chart_data["data"])):
            plt.bar(chart_data["dates"],
                    chart_data["data"][ind],
                    bottom=bottom_sum,
                    color=chart_data["colors"][ind],
                    width=0.4)
            bottom_sum = [sum(val) for val in zip(bottom_sum, chart_data["data"][ind])]

        self.ids.chart_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))   # добавляем диаграмму на виджет
