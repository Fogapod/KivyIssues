# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


class Previous(Screen):

    def on_enter(self):
        '''Вызывается при установке Activity на экран.'''

        app = self.manager._app
        if app:
            app.screen.ids.action_bar.left_action_items = \
                [['menu', lambda x: app.nav_drawer.toggle()]]
            app.screen.ids.action_bar.title = app.title
            Clock.schedule_interval(app.set_banner, 8)

    def on_button_question(self, *args):
        app = self.manager._app
        Clock.unschedule(app.set_banner)

        if app.saved_form:
            app.dialog_restore_form()
        else:
            self.manager.current = 'ask a question'
