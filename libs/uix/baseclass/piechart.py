# -*- coding: utf-8 -*-
#

# region Import
from kivy.uix.screenmanager import Screen

import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
# endregion Import


class PieChart(Screen):
    def on_enter(self):
        pass
        # size_of_groups = [1]    # [12, 11, 3, 30]
        # plt.pie(size_of_groups)
        # center_circle = plt.Circle((0, 0), 0.7, color='white')
        # chart = plt.gcf()
        # chart.gca().add_artist(center_circle)
        # self.ids.chart_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def update_chart(self, chart_data):
        """
        Метод обновления круговой диаграммы PieChart
        @param chart_data: словарь с данные для построения диаграммы. Ключи: data - список с суммами расходов
        по катеогриям; categories_names - наименование категорий расходов; colors - список цветов, которыми будут
        обозначены категории расходов на диаграмме
        @return: None
        """
        figure, axes = plt.subplots()
        # добавляем круговую диаграмму. Радиус внешний окружности = 1, радиус внутренней окружности = 0.45
        axes.pie(chart_data["data"], radius=1, wedgeprops=dict(width=0.45), colors=chart_data["colors"])
        axes.axis('equal')
        # добавляем легенду
        axes.legend(chart_data["categories_names"],
                    fontsize=8,
                    ncol=2,
                    loc='lower center',
                    frameon=False,
                    bbox_to_anchor=(0.5, -0.15))

        # задаем цвет и прозрачность фона диаграммы
        figure.patch.set_facecolor('whitesmoke')
        figure.patch.set_alpha(0.8)

        self.ids.chart_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))   # добавляем диаграмму на виджет
