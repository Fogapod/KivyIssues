# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty


class Previous(Screen):
    
    _app = ObjectProperty()

    def on_enter(self):
        '''Вызывается при установке Activity на экран.'''

        self._app.screen.ids.action_bar.left_action_items = \
            [['menu', lambda x: self._app.nav_drawer._toggle()]]
        self._app.screen.ids.action_bar.title = self._app.title

        self.ids.input_text_form.callback = self._app.callback_for_input_text
