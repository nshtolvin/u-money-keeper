# -*- coding: utf-8 -*-
#

# region Import
from kivy.uix.screenmanager import Screen

import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
# endregion Import


class LineChart(Screen):
    def on_enter(self):
        pass

    def update_chart(self, chart_data):
        """
        Метод обновления круговой диаграммы LineChart
        @param chart_data: словарь с данные для построения диаграммы. Ключи: data - список с суммами расходов
        по катеогриям; categories_names - наименование категорий расходов; colors - список цветов, которыми будут
        обозначены категории расходов на диаграмме
        @return: None
        """
        self.ids.chart_box.clear_widgets()   # очищаем виджет от диаграммы

        # параметры оформления диаграммы
        figure, axes = plt.subplots()
        # задаем цвет и прозрачность фона диаграммы, а также внутренней области диаграммы
        figure.patch.set_facecolor('whitesmoke')
        figure.patch.set_alpha(0.8)
        axes.patch.set_facecolor('whitesmoke')
        axes.patch.set_alpha(0.8)

        # удаляем левую границу области диаграммы
        # axes.spines['left'].set_visible(False)
        axes.spines['top'].set_visible(False)
        axes.spines['right'].set_visible(False)
        axes.spines['bottom'].set_visible(False)

        # добавляем подписи к вертикальной оси диаграммы (поворот меток, выравнивание, размер шрифта)
        plt.yticks(rotation=45, horizontalalignment='right', fontsize=7)

        # добавляем динейчатую диаграмму
        plt.hlines(y=chart_data["categories_names"],
                   xmin=0,
                   xmax=chart_data["data"],
                   colors=chart_data["colors"],
                   linewidth=10)

        # рассчитываем общую сумму расходов, а также долю расходов по каждой из категорий в процентах
        total_sum = sum(chart_data["data"])
        proportions = [round((value / total_sum) * 100, 2) for value in chart_data["data"]]

        # добавляем подписи к каждой линии диаграммы (сумма расходов, доля в %)
        for size, prop, label in zip(chart_data["data"], proportions, chart_data["categories_names"]):
            axes.text(x=size+5, y=label, s=f"{size} ({prop}%)", ha='left', va='center', fontsize=9)
        axes.axes.xaxis.set_ticks([])

        self.ids.chart_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))   # добавляем диаграмму на виджет
