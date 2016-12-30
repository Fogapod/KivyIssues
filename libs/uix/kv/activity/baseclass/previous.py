# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen


class Previous(Screen):

    def on_enter(self):
        '''Вызывается при установке Activity на экран.'''

        app = self.manager._app
        if app:
            app.screen.ids.action_bar.left_action_items = \
                [['menu', lambda x: app.nav_drawer.toggle()]]
            app.screen.ids.action_bar.title = app.title
