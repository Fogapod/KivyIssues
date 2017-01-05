# -*- coding: utf-8 -*-
#
# dialogs.py
#

import os
import types

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.modalview import ModalView

from kivymd.card import MDCard, MDSeparator
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.button import MDFlatButton


def dialog(font_style='Body1', theme_text_color='Secondary', title='Title',
           text='Text', valign='top', dismiss=True, buttons=None,
           ref_callback=None):
    '''Вывод диалоговых окон.'''

    if buttons is None:
        buttons = []

    content = MDLabel(
        font_style=font_style, theme_text_color=theme_text_color,
        text=text, valign=valign, markup=True
    )
    content.bind(size=content.setter('text_size'))
    if ref_callback:
        content.bind(on_ref_press=ref_callback)

    dialog = MDDialog(title=title, content=content, size_hint=(.8, None),
                      height=dp(200), auto_dismiss=dismiss)

    for list_button in buttons:
        text_button, action_button = list_button
        dialog.add_action_button(text_button, action=action_button)
    dialog.open()

    return dialog


def dialog_progress(text_button_cancel='Cancel', text_wait='Wait',
                    events_callback=None, text_color=None):
    if not isinstance(events_callback, types.FunctionType) or \
            isinstance(events_callback, types.MethodType):
        events_callback = lambda x: None
    if not text_color:
        text_color = [0, 0, 0, 1]

    spinner = Builder.template(
        'Progress', text_button_cancel=text_button_cancel,
        text_wait=text_wait, events_callback=events_callback,
        text_color=text_color
    )
    spinner.open()

    return spinner, spinner.ids.label


def file_dialog(title=None, path='.', filter='files', events_callback=None,
                size=None):
    def is_dir(directory, filename):
        return os.path.isdir(os.path.join(directory, filename))

    def is_file(directory, filename):
        return os.path.isfile(os.path.join(directory, filename))

    if not size:
        size = (.7, .5)

    file_manager = FileChooserListView(path=path, filters=['\ *.png'])
    if isinstance(events_callback, types.FunctionType) or \
        isinstance(events_callback, types.MethodType):
        file_manager.ids.layout.ids.button_ok.bind(
            on_release=lambda x: events_callback(file_manager.path))
        file_manager.bind(selection=lambda *x: events_callback(x[1:][0][0]))

    if filter == 'folders':
        file_manager.filters = [is_dir]
    elif filter == 'files':
        file_manager.filters = [is_file]

    dialog = card(file_manager, title, size=size)
    return dialog, file_manager


def card(content, title=None, background_color=None, size=(.7, .5)):
    '''Вывод диалоговых окон с кастомным контентом.'''

    if not background_color:
        background_color = [1.0, 1.0, 1.0, 1]

    card = MDCard(
        size_hint=(1, 1), padding=5, background_color=background_color
    )

    if title:
        box = BoxLayout(orientation='vertical', padding=dp(8))
        box.add_widget(
            MDLabel(
                text=title, theme_text_color='Secondary', font_style="Title",
                size_hint_y=None, height=dp(36)
            )
        )
        box.add_widget(MDSeparator(height=dp(1)))
        box.add_widget(content)
        card.add_widget(box)
    else:
        card.add_widget(content)

    dialog = ModalView(size_hint=size, background_color=[0, 0, 0, .2])
    dialog.add_widget(card)
    dialog.open()

    return dialog
