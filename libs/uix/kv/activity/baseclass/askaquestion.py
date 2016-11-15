# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


class AskAQuestion(Screen):

    def on_enter(self):
        app = self.manager._app

        if app.data.PY2:
            self.ids.issue_field.hint_text = \
                app.data.string_lang_text_issue.decode('utf-8')
        else:
            self.ids.issue_field.hint_text = app.data.string_lang_text_issue

        Clock.unschedule(app.set_banner)
        app.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: app.back_screen(
                app.screen.ids.manager.previous())]]

        if app.set_default_text_check:
            self.ids.add_image.ids.label.text = app.data.string_lang_add_image
            self.ids.add_file.ids.label.text = app.data.string_lang_add_file

    def check_status_fields(self, instance_checker_field,
                            instance_self_field):
        '''Активирует кнопку для отправки вопроса только в том случае,
        если поле темы и поле вопроса заполнены.'''

        if instance_checker_field.text != '' \
                and instance_self_field.text != '':
            self.ids.button_send.disabled = False
            self.manager._app.fill_out_form = True
        else:
            self.ids.button_send.disabled = True
