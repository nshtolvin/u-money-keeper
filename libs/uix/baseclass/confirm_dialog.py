# -*- coding: utf-8 -*-
#

# region Import
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from functools import partial
# endregion Import


class ConfirmDialog(MDDialog):
    # default constructor
    # класс-наследник, использующийся для создания окна подтвержденя удаления расходов пользователя
    def __init__(self, result_func, title='', text='', **kwargs):
        super().__init__(**kwargs)

        # заголовое диалогового окна
        self.title = title
        # текстовое сообщения, передаваемое в диалоговом окне
        self.text = text
        # кнопки диалогового окна
        self.buttons = [
            MDFlatButton(
                text='CANCEL',
                theme_text_color='Custom',
                text_color=self.theme_cls.primary_color,
                on_release=partial(result_func, -1),
            ),
            MDFlatButton(
                text='OK',
                theme_text_color='Custom',
                text_color=self.theme_cls.primary_color,
                on_release=partial(result_func, 0),
            ),
        ]
        if not self.buttons:
            self.ids.root_button_box.height = 0
        else:
            self.ids.root_button_box.height = '30dp'
            self.create_buttons()
