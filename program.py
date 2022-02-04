# -*- coding: utf-8 -*-
#
# The main module initializing the application

# region Import
import os
import sys
from ast import literal_eval

from kivy.lang import Builder
from kivy.core.window import Window
# from kivy.config import ConfigParser
from kivy.clock import Clock
from kivy.utils import get_hex_from_color
from kivy.properties import ObjectProperty, StringProperty

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.card import MDSeparator
from libs.uix.lists_items_lib import (CustomLeftIconButton, CustomTransactionsIconButton,
                                      NewCustomTransactionsIconButton, ScrollViewLabel)

from main import cur_directory
# from libs.translation_lib import Translation
from libs.uix.baseclass.rootscreen import RootScreen
from libs.uix.lists import Lists
from libs.applibs.dialogs import card
from libs.sql_worker_lib import SQLWorker
# endregion Import


class MainApp(MDApp):
    title = 'PROJECT_NAME'
    # icon = 'data/images/icon.png'
    version = '0.0.0'
    nav_drawer = ObjectProperty()
    lang = StringProperty('en')

    # default constructor
    def __init__(self, configurations, **kwargs):
        # base class initialization
        super(MainApp, self).__init__(**kwargs)
        # set up the connection of the application with the keyboard (связь приложения и клавиатуры)
        # Основное окно приложения (может быть только одно)
        Window.bind(on_keyboard=self.events_program)
        # поведение содержимого окна при отображении виртуальной клавиатуры на мобильных платформах
        # окно сдвигается так, что текущий целевой виджет TextInput, запрашивающий клавиатуру, отображается
        # чуть выше виртуальной клавиатуры
        Window.soft_input_mode = 'below_target'

        self.list_previous_screens = ['main']
        self.__window = Window
        self.configurations = configurations    # конфигурация приложения # ConfigParser()
        self.__app_screen = None
        self.__scr_manager = None
        self.window_language = None
        self.exit_interval = False
        self.dict_language = literal_eval(
            open(os.path.join(self.directory, 'data', 'locales', 'locales.txt')).read()
        )
        # Временно удалено. Также везде удалено self.translation.tr(...) или app.translation.tr(...)
        # self.translation = Translation(
        #     self.lang, 'Ttest', os.path.join(self.directory, 'data', 'locales')
        # )
        self.__sql_worker = SQLWorker(cur_directory, self.configurations["DB_FILENAME"])
        # объект, в котором хранятся данные о странице ввода расходов (содержит цифровую клавиатуру,
        # окна ввода суммы расходов и заметок)
        self.__consumption_entry_sheet = None
        # назначение страницы ввода расходов ('new' - новые данные/ 'edit' - изменение транзакции)
        self.__consumption_sheet_purpose = None
        # данные редактируемой транзакции (только для self.__consumption_sheet_purpose=='edit'
        self.__edited_transaction_data = None
        # картеж с данными о категории расходов, траты по которой записываются в БД приложения - (ctg_id, ctg_name)
        self.__current_category = None
        # Картеж из двух дат: (первый день месяца, последний день месяца). По умолчанию эти даты рассчитываются
        # исходя из текщего месяца. Поле может быть изменено при обращении к календарю и выбору произвольной даты -
        # значения картежа автоматически будут пересчитаны
        self.__current_date = None

    def build(self):
        """
        Метод для инициализации приложения. Возвращает объект Widget (виджет/дерево), используемый в качестве
        корневого виджета и добавлен в окно приложения; или None
        """
        self.set_value_from_configurations()
        self.load_all_kv_files(os.path.join(self.directory, 'libs', 'uix', 'kv'))
        # тема и цветовая палитра приложения
        # self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        # self.theme_cls.primary_hue = "600"
        self.__app_screen = RootScreen()
        self.__scr_manager = self.__app_screen.ids.scr_manager
        # панель навигации приложения
        self.nav_drawer = self.__app_screen.ids.nav_drawer
        return self.__app_screen

    # def get_application_config(self):
    #     return super(MainApp, self).get_application_config('{}/%(appname)s.ini'.format(self.directory))

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'language', 'en')

    def set_value_from_configurations(self):
        """ Метод, считывающий параметры приложения из файла """
        # self.config.read(os.path.join(self.directory, 'main.ini'))
        # self.lang = self.config.get('General', 'language')
        self.title = self.configurations["PROJECT_NAME"]
        self.version = self.configurations["VERSION"]

    def load_all_kv_files(self, directory_kv_files):
        """
        Метод чтения kv-файлов из указнного каталога. На основе каждого файла создается объект Builder - виджет
        """
        for kv_file in os.listdir(directory_kv_files):
            kv_file = os.path.join(directory_kv_files, kv_file)
            if os.path.isfile(kv_file):
                with open(kv_file, encoding='utf-8') as kv:
                    Builder.load_string(kv.read())

    def events_program(self, instance, keyboard, keycode, text, modifiers):
        pass
        # if keyboard in (1001, 27):
        #     if self.nav_drawer.state == 'open':
        #         self.nav_drawer.set_state('toggle')
        #     self.back_screen(event=keyboard)
        # elif keyboard in (282, 319):
        #     pass
        # return True

    def back_screen(self, event=None):
        if event in (1001, 27):
            if self.__scr_manager.current == 'main':
                self.dialog_exit()
                return
            try:
                self.__scr_manager.current = self.list_previous_screens.pop()
            except:
                self.__scr_manager.current = 'main'
            self.__app_screen.ids.action_bar.title = self.title
            # "self.nav_drawer.toggle_nav_drawer()]]" заменено на "self.nav_drawer.set_state('toggle')"
            self.__app_screen.ids.action_bar.left_action_items = \
                [['menu', lambda x: self.nav_drawer.set_state('toggle')]]

    def dialog_exit(self):
        def check_interval_press(interval):
            self.exit_interval += interval
            if self.exit_interval > 5:
                self.exit_interval = False
                Clock.unschedule(check_interval_press)

        if self.exit_interval:
            sys.exit(0)
        Clock.schedule_interval(check_interval_press, 1)
        toast('Press Back to Exit')

    def show_about(self, *args):
        self.nav_drawer.set_state('toggle')
        about_content = open(os.path.join(self.directory, 'data', 'ABOUT'), encoding='utf-8').read()
        self.__app_screen.ids.about.ids.label.text = about_content.format(
            version=self.version,
            link_color=get_hex_from_color(self.theme_cls.primary_color)
        )
        self.__scr_manager.current = 'about'
        self.__app_screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(27)]]

    def show_license(self, *args):
        self.nav_drawer.set_state('toggle')
        self.__app_screen.ids.license.ids.text_license.text = \
            '%s' % open(os.path.join(self.directory, 'data', 'LICENSE'), encoding='utf-8').read()
        self.__scr_manager.current = 'license'
        self.__app_screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(27)]]
        self.__app_screen.ids.action_bar.title = 'MIT LICENSE'

    def select_locale(self, *args):
        def select_locale(name_locale):
            for locale in self.dict_language.keys():
                if name_locale == self.dict_language[locale]:
                    self.lang = locale
                    self.configurations.set('General', 'language', self.lang)
                    self.configurations.write()

        dict_info_locales = {}
        for locale in self.dict_language.keys():
            dict_info_locales[self.dict_language[locale]] = \
                ['locale', locale == self.lang]

        if not self.window_language:
            self.window_language = card(
                Lists(
                    dict_items=dict_info_locales,
                    events_callback=select_locale, flag='one_select_check'
                ),
                size=(.85, .55)
            )
        self.window_language.open()

    def on_start(self):
        import datetime
        from calendar import monthrange

        # формируем картеж дат, которые будет использовать приложение. Так как данный методы вызывается при запуске
        # приложения, то по умолчанию определяется текщая дата, исходя из которой рассчитывается первый и последний
        # день текущего месяца
        today = datetime.datetime.today()
        # определяем картеж: (день недели первого дня месяца, количество дней в месяце)
        month_range = monthrange(today.year, today.month)
        # формируем картеж с датами для работы приложения
        self.__current_date = (
            datetime.date(today.year, today.month, 1),
            datetime.date(today.year, today.month, month_range[1])
        )
        # загружаем данные в приложение, обновляем страницы
        self.__update_application_screens()

    def show_notification(self, *args):
        # TODO: добавить обработчики кнопок на панели навигации
        toast('Functionality coming soon')

    def __update_application_screens(self):
        """
        Метод, обеспечивающий формирование данных для инициализации ими приложения. К локальной БД выпоняется ряд
        запросов, формирующие соответствующие выборки трат для CategoriesScreen, TransactionsScreen, StatisticsScreen
        с учетом заданного диапазона дат. Каждый запрос возвращает список картежей. Далее эти списки обрабатываются
        в отдельных методах для наполнения виджетами (кнопки, графики, диаграммы и прочее).
        @return: None
        """
        from threading import Thread

        # результат выборки для CategoriesScreen
        # (также используется для построения линейчатой диаграммы LineChart на StatisticsScreen)
        transactions_for_categories_screen = self.__sql_worker.make_select_for_categories_screen(
            from_date=self.__current_date[0],
            to_date=self.__current_date[1]
        )
        # инициализация потока, обеспечивающего обработку выборки и загрузку виджетов для CategoriesScreen
        categories_screen_thread = Thread(
            target=self.__update_categories_screen(transactions_for_categories_screen),
            # args=(bot_settings_1.settings, bot_users, ),
            name='CetegScrThread',
            daemon=True)

        # результат выборки для TransactionsScreen
        # (аналогичная выборка используется для построения столбчатой диаграммы с накоплением на StatisticsScreen)
        transactions_for_transactions_screen = self.__sql_worker.make_select_for_transactions_screen(
            from_date=self.__current_date[0],
            to_date=self.__current_date[1]
        )
        # инициализация потока, обеспечивающего обработку выборки и загрузку виджетов для TransactionsScreen
        transactions_screen_thread = Thread(
            target=self.__update_transactions_screen(transactions_for_transactions_screen),
            name='TransactionsScrThread',
            daemon=True)

        # результат выборки для построения столбчатой диаграммы с накоплением на StatisticsScreen (обязательно
        # осуществляется сортировка результатов по возрастанию дат транзакций
        transactions_for_bar_chart = self.__sql_worker.make_select_for_transactions_screen(
            from_date=self.__current_date[0],
            to_date=self.__current_date[1],
            sort_type='ASC'
        )
        # инициализация потока, обеспечивающего обработку выборки и загрузки виджета BarChart для StatisticsScreen
        bar_chart_thread = Thread(
            target=self.__update_bar_chart_on_statistics_screen(transactions_for_bar_chart),
            name='BarChartThread',
            daemon=True)

        # инициализация потока, обеспечивающего обработку выборки и загрузку виджета LineChart для StatisticsScreen
        line_chart_thread = Thread(
            target=self.__update_line_chart_on_statistics_screen(transactions_for_categories_screen),
            name='LineChartThread',
            daemon=True)

        # запуск всех потоков по обработке данных и инициализации виджетами страниц приложения
        categories_screen_thread.start()
        categories_screen_thread.join()

        transactions_screen_thread.start()
        transactions_screen_thread.join()

        bar_chart_thread.start()
        bar_chart_thread.join()

        line_chart_thread.start()
        line_chart_thread.join()

    def __update_categories_screen(self, transactions):
        """
        Метод обновления страницы с категориями расходов - CategoriesScreen. Обновляются кнопки и диаграмма PieChart
        Так как для построения LineChart используется аналогичный подход обработки данных, то в этом же методе
        обновляется диаграмма LineChart на StatisticsScreen
        @param transactions: список с данными (транзакции) о расходах
        @return: None
        """
        from math import ceil
        from functools import partial

        # предварительная очистка кнопок на экране с категориями трат
        left_btn_list = self.root.ids.main.ids.categories_screen.ids.left_btn_list
        left_btn_list.clear_widgets()
        right_btn_list = self.root.ids.main.ids.categories_screen.ids.right_btn_list
        right_btn_list.clear_widgets()

        # определяем середину списка с данными, чтобы далее распределить кнопки с категориями по правую и левую
        # стороны от диаграммы PieChart
        records_half_index = ceil(len(transactions) / 2)
        # словарь, в котором хранятся данные для построения диаграммы PieChart и LineChart. Ключи:
        # data - список с суммами расходов по катеогриям (длина дуги окружности или длина линии)
        # categories_names - наименование категорий расходов (для легенды или значения по вертикальной оси)
        # colors - список цветов, которыми будут обозначены категории расходов на диаграмме
        chart_data = {"data": list(), "categories_names": list(), "colors": list()}
        for rec in transactions:
            # определяем в какую группу кнопок (правую или левую относительно диаграммы) будет добавена кнопка
            # с категорией: если индекс просматриваемой записи с категорией трат меньше среднего, то
            # кнопка добавляется слева от диаграммы, иначе - справа от диаграммы
            current_half = left_btn_list if transactions.index(rec) < records_half_index else right_btn_list
            current_half.add_widget(
                CustomLeftIconButton(
                    icon=rec[2],
                    text=rec[1],
                    secondary_text=str(rec[3]),
                    # events_callback=lambda x: self.show_consumption_entry_sheet(rec[1])
                    # events_callback=partial(self.show_consumption_entry_sheet, rec[1])
                    events_callback=partial(self.show_consumption_entry_sheet, 'new',
                                            {"transaction_date": None,
                                             "category": rec[1]})
                )
            )
            # если по категории были потрачены средства, то добавляем данную категорию
            # и траты по ней в соответсвующие списки (для построения диаграммы)
            if rec[3] != 0:
                chart_data["data"].append(rec[3])
                chart_data["categories_names"].append(rec[1])   # labels
                chart_data["colors"].append(rec[4])
        if len(chart_data["categories_names"]) != 0:
            # обновляем диаграмму PieChart
            self.root.ids.main.ids.categories_screen.ids.pie_chart.update_chart(chart_data)
        # обновляем итоговую сумму расходов
        self.root.ids.main.ids.categories_screen.ids.lbl_total.text = 'Total costs: %.2f' % (sum(chart_data["data"]))

    def __update_transactions_screen(self, transactions):
        """
        Метод обновления страницы с категориями расходов - TransactionsScreen. Обновляется список транзакций
        @param transactions: список с данными (транзакции) о расходах
        @return: None
        """
        from datetime import datetime
        from functools import partial

        transactions_btn_list = self.root.ids.main.ids.transactions_screen.ids.transactions_btn_list
        transactions_btn_list.clear_widgets()
        separator_date = None   # разделительная дата. Используется для отделения трат по отдельным датам
        for rec in transactions:
            curr_date = datetime.strptime(rec[5], "%Y-%m-%d")
            # если дата рассматриваемой транзакции отличается от даты-сепаратора, то добавляется разделительная черта,
            # новая дата для ряда транзакций
            if curr_date != separator_date:
                transactions_btn_list.add_widget(MDSeparator())
                transactions_btn_list.add_widget(ScrollViewLabel(text=curr_date.strftime("%d %b %Y (%a)")))
                separator_date = curr_date   # одновляем разделительную дату
            # добавляем кнопки с транзакциями
            transactions_btn_list.add_widget(
                NewCustomTransactionsIconButton(
                    icon=rec[0],
                    text=rec[1],
                    secondary_text=str(-1 * rec[2]),
                    tertiary_text=rec[3],
                    events_callback=partial(self.show_consumption_entry_sheet, 'edit',
                                            {"transaction_id": rec[4],
                                             "transaction_date": separator_date,
                                             "category": rec[1],
                                             "cost": str(rec[2]),
                                             "note": rec[3]}),
                    delete_callback=partial(self.show_confirm_dialog_to_delete,
                                            {"transaction_id": rec[4],
                                             "transaction_date": separator_date,
                                             "category": rec[1],
                                             "cost": str(rec[2]),
                                             "note": rec[3]})
                )
            )

    def __update_bar_chart_on_statistics_screen(self, transactions):
        """
        Метод обновления столбчатой диаграммы BarChart на странице со статистикой расходов - StatisticsScreen
        @param transactions: список с данными (транзакции) о расходах
        @return: None
        """
        from datetime import datetime

        # словарь, в котором хранятся данные для построения диаграммы BarChart. Ключи:
        # data - список с суммами расходов по катеогриям (высота столбца)
        # dates - список с датами в которые осуществлялись расходы (значения по горизонтальной оси)
        # colors - список цветов, которыми будут обозначены категории расходов на диаграмме
        chart_data = {"data": list(), "dates": list(), "colors": list()}
        # список с данными по всем категориям трат. Разбивается на отдельные списки для построения диаграммы
        all_category = self.__sql_worker.get_all_category()
        category_name = [item[0] for item in all_category]
        chart_data["colors"] = [item[1] for item in all_category]

        separator_date = None   # разделительная дата. Используется для отделения трат по отдельным датам
        # список с данными о расходах. Длина списка определяется количеством категорий расходов
        one_bar_data = list()
        # в цикле перебираем все транзакции и формируем ПРЕДВАРИТЕЛЬНЫЙ двумерный массив со значениями расходов.
        # Каждая строка - расходы по категориям в рамках одной даты. Все строки одинаковой длины, которая
        # определяется количеством категорий расходов. Например, для 3-х дат и 4-х категрий расходов двумерный массив
        # может выглядеть так: [[0, 2, 4, 6], [1, 0, 0, 0], [0, 5, 0, 4]]. Т.е. в первый день траты были по 2-ой, 3-ей
        # и 4-ой категории, во второй - только по 1-ой категории, а в третий день - по 2-ой и 4-ой категории.
        for rec in transactions:
            curr_date = datetime.strptime(rec[5], "%Y-%m-%d")
            # если дата рассматриваемой транзакции отличается от даты-сепаратора, то она добавляется в список dates
            if curr_date != separator_date:
                chart_data["dates"].append(curr_date.strftime("%d %b"))  # %Y
                separator_date = curr_date   # одновляем разделительную дату

                # смена даты-сепаратора обозначет, что строка двумерного массива с данными расходо заполнена
                # добавляем ее в конечный двумерный массив с данными
                if len(one_bar_data) != 0:
                    chart_data["data"].append(one_bar_data.copy())
                # обнуляем список со значениями расходов. Длина списка определяется количеством категорий расходов
                one_bar_data = [0] * len(category_name)
            # в список со значениями расходов добавляем сумму транзакции - сумма транзакции записиывается в позицию,
            # индекс которой совпадает с индексом категории расходов в списке category_name
            one_bar_data[category_name.index(rec[1])] += rec[2]
        # добавляем полседнюю строку в двумерный массив с расходами
        chart_data["data"].append(one_bar_data.copy())

        # для построения диаграммы требуется "поврнуть" массив на 90градусов (или считать его по столбцам или
        # транспонировать матрицу). Например, рассмотренный массив примет вид:
        # [[0, 1, 0], [2, 0, 5], [4, 0, 0], [6, 0, 4]]. Т.е. теперь в каждой строке это значения трат по каждой
        # категории, а в столбцах - даты совершения расходов
        chart_data["data"] = [list(i) for i in zip(*chart_data["data"])]
        # обновляем диаграмму BarChart
        if len(chart_data["dates"]) != 0:
            self.root.ids.main.ids.statistics_screen.ids.bar_chart.update_chart(chart_data)

    def __update_line_chart_on_statistics_screen(self, transactions):
        """
        Метод обновления линейчатой диаграммы LineChart на странице со статистикой расходов - StatisticsScreen
        @param transactions: список с данными (транзакции) о расходах
        @return: None
        """
        # для построения диаграммы требуется отсортировать список транзакций (список картежей) по убыванию расходов
        sorted_transactions_by_costs = sorted(transactions, key=lambda tup: tup[3])

        # словарь, в котором хранятся данные для построения диаграммы LineChart. Ключи:
        # data - список с суммами расходов по катеогриям (длина линии)
        # categories_names - наименование категорий расходов (значения по вертикальной оси)
        # colors - список цветов, которыми будут обозначены категории расходов на диаграмме
        chart_data = {"data": list(), "categories_names": list(), "colors": list()}
        for rec in sorted_transactions_by_costs:
            if rec[3] == 0:
                continue
            chart_data["data"].append(rec[3])
            chart_data["categories_names"].append(rec[1])
            chart_data["colors"].append(rec[4])
        # обновляем диаграмму LineChart
        if len(chart_data["categories_names"]) != 0:
            self.root.ids.main.ids.statistics_screen.ids.line_chart.update_chart(chart_data)

    def show_consumption_entry_sheet(self, purpose, data):
        """
        Метод вызова окна ввода/редактирования данных о расходах (сумма расходов, заметки)
        @param purpose: назначение окна ввода (new - ввод новой транзакции расходов, edit - изменение данных)
        @param data: словарь с параметрами для инициализации окна ввода. Ключи:
        transaction_id - идентификатор редактируемой транзакции из БД приложения (только для purpose==edit)
        transaction_date - дата совершения транзакции (только для purpose==edit)
        category - наименование категории расходов
        cost - сумма расходов (0 для новой транзакции, иначе - значение транзакции с указанным transaction_id)
        note - заметка (пусто для новой транзакции, иначе - значение транзакции с указанным transaction_id)
        @return: None
        """
        from kivymd.uix.bottomsheet import MDCustomBottomSheet
        from libs.uix.baseclass.consumptionentry_sheet import СonsumptionEntrySheet

        # и нициализация и вызов окна для ввода/редактирования данных транзакциии
        self.__consumption_entry_sheet = MDCustomBottomSheet(screen=СonsumptionEntrySheet())
        self.__consumption_entry_sheet.open()
        self.__current_category = self.__sql_worker.get_category_id(data["category"])[0]
        # при добавлении новой транзакции добавляем только лейбел с наименование категории расходов
        self.__consumption_entry_sheet.screen.ids.lbl_consumption_category.text = self.__current_category[1]
        # при редактировании расходов на окно ввода/редактирования переносятся сумма расходов и заметки
        if purpose == 'edit':
            self.__consumption_entry_sheet.screen.ids.lbl_consumption.text = data["cost"]
            self.__consumption_entry_sheet.screen.ids.transaction_note.text = data["note"]
        # параметры окна ввода/редактирования данных о расходах сохраняем
        self.__consumption_sheet_purpose = purpose
        self.__edited_transaction_data = data.copy()
    
    def update_consumption_value(self, symbol):
        """
        Метод обработки ввода суммы расходов с цифровой клавиатуры
        @param symbol: введенный (выбранный) символ с цифровой клавиатуры
        @return: обновляется сумма расходов, отображаемая в объекте MDLabel id:lbl_consumption
        """

        cons_value = self.__consumption_entry_sheet.screen.ids.lbl_consumption.text
        # по нажатию backspace из строки удаляется последний символ
        # в прочих случаях новый символ добавляется в конец строки с расходами
        if symbol == '<--':
            cons_value = cons_value[:len(cons_value)-1]
        elif symbol == 'OK':
            import datetime

            # параметры отбработчика кнопки OK. Зависят от того вводились новые данные о расходах (ключ 'new') или
            # редактировались (ключ 'edit') уже существующие данные
            # date - дата транзакции (для новых - ссегодняшняя дата, для редактировани - дата из БД)
            # func - имя вызываемой функции (для создания новой записи в БД или редактирования существующей)
            # msg - выводимый результат выполнения операции
            options = {"new": {"date": datetime.date.today(),
                               "func": self.__sql_worker.insert_new_transaction_data,
                               "msg": 'Data added!'},
                       "edit": {"date": self.__edited_transaction_data["transaction_date"],
                                "func": self.__sql_worker.update_transaction_data,
                                "msg": 'Data updated!'}
                       }
            # формируем картеж с данными о расходах
            transaction_data = (self.__current_category[0],
                                options[self.__consumption_sheet_purpose]["date"].strftime("%Y%m%d"),
                                round(float(cons_value)),
                                self.__consumption_entry_sheet.screen.ids.transaction_note.text)
            # при редактировании транзакции последним (4ым элементом) добавляем id редактируемой транзакции из БД
            if self.__consumption_sheet_purpose == 'edit':
                transaction_data = transaction_data + (self.__edited_transaction_data["transaction_id"],)

            if transaction_data[3] != 0:
                # result = self.__sql_worker.insert_new_transaction_data(transaction_data)
                result = options[self.__consumption_sheet_purpose]["func"](transaction_data)
            else:
                result = [-1]
            toast(options[self.__consumption_sheet_purpose]["msg"] if len(result) == 0 else
                  'Error! Perhaps a null value was entered. Something went wrong.')

            self.__update_application_screens()

            self.__consumption_entry_sheet.dismiss()
            self.__current_category = None
        else:
            cons_value = f"{cons_value}{symbol}"

        # дополнительные проверки при вводе данных о расходах
        # если не вводиться дробь меньше 0, то нули в начале строки удаляются
        if cons_value[:2] != '0.':
            cons_value = cons_value.lstrip('0')
        # допускается ввод только одной точки, отделяющей целую и дробную часть вводимого числа
        if cons_value.count('.') > 1:
            cons_value = cons_value[:-1]
        # если в результате уделения всех знаяений строка пустая, то значение расходов заполняется нулем
        # также не допускается ввод нескольких нулей
        if len(cons_value) == 0 or cons_value == '0':
            cons_value = '0'
        self.__consumption_entry_sheet.screen.ids.lbl_consumption.text = cons_value

    def show_confirm_dialog_to_delete(self, data):
        """
        Метод для осуществления удаления выбранной транзакции с расходами. Перед удалением появляется окно
        подтверждения операции. При положительном ответе пользователя транзакция удаляется, в остальных случаях - нет.
        @param data: словарь с параметрами удаляемой транзакции расходов. Ключи:
        transaction_id - идентификатор редактируемой транзакции из БД приложения (только для purpose==edit)
        transaction_date - дата совершения транзакции (только для purpose==edit)
        category - наименование категории расходов
        cost - сумма расходов (0 для новой транзакции, иначе - значение транзакции с указанным transaction_id)
        note - заметка (пусто для новой транзакции, иначе - значение транзакции с указанным transaction_id)
        @return: None
        """
        from libs.uix.baseclass.confirm_dialog import ConfirmDialog

        def get_dialog_result(dialog_result, *args):
            """
            Метод, обрабатывающий результат выбора пользователя по удалению/нет транзакции с расходами. При
            положительном ответе пользователя транзакция удаляется, в остальных случаях - нет.
            @param dialog_result: ответ пользователя: 0 - пользователь нажал OK, -1 - пользователь нажал CANCEL
            @param args:
            @return: None; если dialog_result == 0, то транзакции удаляется, в остальных случаях нет.
            """
            # если пользователь нажал OK, то транзакция удаляется
            if dialog_result == 0:
                transaction_data = (data["transaction_id"], data["transaction_date"].strftime("%Y%m%d"))
                result = self.__sql_worker.delete_transaction_data(transaction_data)
                toast('Data deleted!' if len(result) == 0 else 'Error! Something went wrong.')
                # после удаления обновляем страницы (экраны) приложения
                self.__update_application_screens()
            # диалоговое окно подтверждения операции удаления транзакции скрывается
            dialog.dismiss()

        # вызываем диалоговое окно для подтверждения удаления транзакции с расходами
        dialog = ConfirmDialog(
            title='Delete transaction?',
            text='Are you sure you want to delete the transaction?',
            result_func=get_dialog_result,
        )
        dialog.open()

    def show_calendar(self):
        """
        Вызов Календаря для выбора дат
        @return: None
        """
        from kivymd.uix.picker import MDDatePicker

        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_calendar_save, on_cancel=self.on_calendar_cancel)
        date_dialog.open()

    def on_calendar_save(self, instance, value, date_range):
        """
        Обработчик кнопки OK на окне выбора дат (Календарь)
        @param instance:
        @param value: выбранная дата Календаря
        @param date_range: выбранный диапазон дат Календаря (для mode="range")
        @return: None
        """
        from datetime import date
        from calendar import monthrange

        # print(instance, value, date_range)
        # обновляем картеж дат, которые будет использовать приложение. Картеж формируется исходя из произвольно
        # выбранной даты: пользователь выбирает произвольную дату, указывая скорее на месяц, который его интересует.
        # Далее определяется первый и последний день выбранного месяца
        month_range = monthrange(value.year, value.month)
        # формируем картеж с датами для работы приложения
        self.__current_date = (
            date(value.year, value.month, 1),
            date(value.year, value.month, month_range[1])
        )
        # загружаем данные в приложение
        self.__update_application_screens()

    def on_calendar_cancel(self, instance, value):
        """
        Обработчик кнопки CANCEL на окне выбора дат (Календарь)
        @param instance:
        @param value: выбранная дата Календаря
        @return: None
        """
        pass

    # def on_lang(self, instance, lang):
    #     self.translation.switch_lang(lang)
