# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


class Previous(Screen):

    def on_enter(self):
        '''Вызывается при установке Activity на экран.'''

        if self.manager._app:
            self.manager._app.screen.ids.action_bar.left_action_items = \
                [['menu', lambda x: self.manager._app.nav_drawer.toggle()]]
            self.manager._app.screen.ids.action_bar.title = \
                self.manager._app.title
            Clock.schedule_interval(self.manager._app.set_banner, 8)

    def on_button_question(self, *args):
        Clock.unschedule(self.manager._app.set_banner)
        self.manager._app.screen.ids.manager.current = 'ask a question'
