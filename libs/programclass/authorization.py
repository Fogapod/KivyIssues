# -*- coding: utf-8 -*-

import os
import threading

from kivy.clock import Clock

from libs.createpreviousportrait import create_previous_portrait
from libs import vkrequests as vkr

from kivymd import snackbar


class GetAndSaveLoginPassword(object):

    def get_fields_login_password(self):
        login = self.input_dialog.ids.login.text
        password = self.input_dialog.ids.password.text
        return login, password

    def check_fields_login_password(self, text_button):
        login, password = self.get_fields_login_password()

        if login == '' or login.isspace():
            msg = self.data.string_lang_field_login_empty
            snackbar.make(msg)
            return
        if password == '' or password.isspace():
            msg = self.data.string_lang_field_password_empty
            snackbar.make(msg)
            return

        self.input_dialog.dismiss()
        self.save_login_password(login, password)

    def save_login_password(self, login, password):
        # TODO: Добавить кодировку логина и пароля.
        self.data.regdata['login'] = login
        self.data.regdata['password'] = password
        self.config.set('General', 'regdata', self.data.regdata)
        self.config.write()
        self._authorization_on_vk(login, password)


class AuthorizationOnVK(object):

    def _authorization_on_vk(self, login, password):
        def _authorization_on_vk(interval):
            thread_authorization = threading.Thread(
                target=self.authorization_on_vk, args=(login, password,)
            )
            thread_authorization.start()

        Clock.schedule_once(lambda x: self.show_progress(
            self.data.string_lang_authorization,
            self.dialog_on_fail_authorization), 0)
        Clock.schedule_once(_authorization_on_vk, 1)

    def authorization_on_vk(self, login, password):
        result, info = vkr.log_in(login=login, password=password)

        if not result:
            self.dialog_on_fail_authorization()
            self.open_dialog(
                text=self.data.string_lang_error_auth.format(info),
                dismiss=True
            )

        else:
            self.config.set('General', 'authorization', 1)
            self.config.write()

            if not os.path.exists(
                    '{}/data/images/avatar.png'.format(self.directory)):
                self.load_avatar()
            if self.data.user_name == 'User':
                self.set_user_name()
            self.set_issues_in_group()

            self.dialog_authorization.dismiss()
            self.screen.ids.previous.ids.button_question.bind(
                on_release=self.screen.ids.previous.on_button_question)

    def load_avatar(self):
            self.instance_text_authorization.text = \
                self.data.string_lang_load_avatar
            avatar, info = vkr.get_user_photo(size='max')

            if avatar:
                path_to_avatar_origin = \
                    '{}/data/images/avatar_origin.png'.format(self.directory)
                path_to_avatar_portrait = \
                    '{}/data/images/avatar.png'.format(self.directory)
                with open(path_to_avatar_origin, 'wb') as avatar_origin:
                    avatar_origin.write(avatar)

                create_previous_portrait(
                    path_to_avatar_origin, path_to_avatar_portrait
                )
                os.remove(path_to_avatar_origin)
                Clock.schedule_once(lambda x: self.set_avatar(
                    path_to_avatar_portrait), 1)

    def set_user_name(self):
        self.instance_text_authorization.text = \
            self.data.string_lang_load_user_name
        name, info = vkr.get_user_name()

        if name:
            self.config.set('General', 'user_name', name)
            self.config.write()
            self.nav_drawer.ids.user_name.text = name

    def set_issues_in_group(self):
        self.instance_text_authorization.text = \
            self.data.string_lang_load_issues_in_group
        issues_in_group, info = vkr.get_issue_count()

        if issues_in_group:
            if issues_in_group > self.data.issues_in_group:
                new_issues = str(issues_in_group - self.data.issues_in_group)
                self.nav_drawer.ids.new_issues_in_group.text = \
                    self.data.string_lang_new_issues_in_group.format(
                        new_issues
                    )
                self.screen.ids.action_bar.right_action_items = \
                    [['comment-plus-outline',
                      lambda x: self.manager.screens[2].show_posts(
                          new_issues)]]
            else:
                self.nav_drawer.ids.new_issues_in_group.text = \
                    self.data.string_lang_new_issues_in_group.format('0')

            self.config.set('General', 'issues_in_group', issues_in_group)
            self.config.write()
            self.nav_drawer.ids.issues_in_group.text = \
                self.data.string_lang_issues_in_group.format(
                    str(issues_in_group)
                )
