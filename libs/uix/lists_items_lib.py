# -*- coding: utf-8 -*-
#

# region Import
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.properties import (
    ObjectProperty,
    StringProperty,
)

from kivymd.theming import ThemableBehavior
from kivymd.uix.button import (
    MDIconButton
)
from kivymd.uix.list import (
    ILeftBody,
    ILeftBodyTouch,
    OneLineIconListItem,
    TwoLineIconListItem,
    ThreeLineIconListItem,
)
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCardSwipe
# endregion Import


class LeftIcon(ILeftBody, Image):
    pass


class LeftMDIcon(ILeftBodyTouch, MDIconButton):
    pass


class RightMDIcon(ILeftBodyTouch, MDIconButton):
    pass


class CustomNavDrawerButton(OneLineIconListItem, ThemableBehavior):
    icon = StringProperty()
    events_callback = ObjectProperty()


class CustomLeftIconButton(TwoLineIconListItem, ThemableBehavior):
    icon = StringProperty()
    events_callback = ObjectProperty()


class CustomTransactionsIconButton(ThreeLineIconListItem, ThemableBehavior):
    icon = StringProperty()
    events_callback = ObjectProperty()


class NewCustomTransactionsIconButton(MDCardSwipe, ThemableBehavior):
    icon = StringProperty()
    text = StringProperty()
    secondary_text = StringProperty()
    tertiary_text = StringProperty()
    events_callback = ObjectProperty()
    delete_callback = ObjectProperty()


class ScrollViewLabel(MDLabel, ThemableBehavior):
    pass


kv_description = \
"""
<CustomNavDrawerButton>:
    divider: None
    text_color: self.theme_cls.text_color
    on_release: root.events_callback()

    IconLeftWidget:
        icon: root.icon
        text_color: root.text_color


<CustomLeftIconButton>:
    divider: None
    text_color: self.theme_cls.text_color
    on_release: root.events_callback()
    height: dp(60)

    IconLeftWidget:
        icon: root.icon
        text_color: root.text_color


<CustomTransactionsIconButton>:
    divider: None
    text_color: self.theme_cls.text_color
    secondary_theme_text_color: 'Custom'
    secondary_text_color: '#f01111'
    on_release: root.events_callback()

    IconLeftWidget:
        icon: root.icon
        text_color: root.text_color


<NewCustomTransactionsIconButton>:
    size_hint_y: None
    height: btn.height

    MDCardSwipeLayerBox:
        padding: '8dp'
        MDIconButton:
            icon: 'trash-can'
            pos_hint: {'center_y': .5}
            on_release: root.delete_callback()

    MDCardSwipeFrontBox:
        
        ThreeLineIconListItem:
            id: btn
            text: root.text
            secondary_text: root.secondary_text
            tertiary_text: root.tertiary_text
            divider: None
            text_color: self.theme_cls.text_color
            secondary_theme_text_color: 'Custom'
            secondary_text_color: '#f01111'
            bg_color: '#fafafa'
            _no_ripple_effect: True
            on_release: root.events_callback()
            
            IconLeftWidget:
                icon: root.icon


<ScrollViewLabel>:
    halign: 'left'
    font_size: '1sp'
    bold: True
    theme_text_color: 'Custom'
    text_color: self.theme_cls.primary_color
    size_hint_y: None
    height: dp(30)
"""

Builder.load_string(kv_description)

# class CstmRightIconButton(BoxLayout, ButtonBehavior, ThemableBehavior):
#     text = StringProperty()
#     secondary_text = StringProperty()
#     icon = StringProperty()
#     on_release = ObjectProperty()
# <CstmRightIconButton>:
#     orientation: 'horizontal'
#     size_hint: 1, None
#     padding: [dp(20), 0, 0, 0]
#     height: dp(55)
#     on_release: app.no_action_function
#
#     MDIcon:
#         icon: root.icon
#         size_hint_x: .35
#
#     BoxLayout:
#         orientation: 'vertical'
#         size_hint_x: .65
#
#         MDLabel:
#             text: root.text
#             halign: 'left'
#             text_color: None
#             font_style: 'Subtitle1'
#             font_size: 15
#             theme_text_color: 'Primary'
#         MDLabel:
#             text: root.secondary_text
#             halign: 'left'
#             text_color: None
#             font_style: 'Body1'
#             font_size: 14
#             theme_text_color: 'Secondary'
