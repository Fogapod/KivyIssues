# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

from libs.vkrequests import create_issue


class Previous(Screen):
    
    _app = ObjectProperty()

    def on_enter(self):
        '''Вызывается при установке Activity на экран.'''

        self._app.screen.ids.action_bar.left_action_items = \
            [['menu', lambda x: self._app.nav_drawer.toggle()]]
        self._app.screen.ids.action_bar.title = self._app.title

        self.ids.input_text_form.callback = self.callback_for_input_text

    def callback_for_input_text(self, flag):
        if flag in ('FILE', 'FOTO'):
            self._app.add_content(flag)
        elif flag == 'SEND':
            # result, text_error = create_issue(
            #    {'file': None, 'image': None, 'issue': 'Text message...',
            #     'theme': ''}
            # )
            # print(result, text_error)
            pass
