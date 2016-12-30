# -*- coding: utf-8 -*-

import os
import threading

from kivy.clock import Clock

from libs.createpreviousportrait import create_previous_portrait
from libs import vkrequests as vkr


class GetAndSaveLoginPassword(object):

    def get_fields_login_password(self):
        login = self.input_dialog.ids.login.text
        password = self.input_dialog.ids.password.text

        return login, password

    def check_fields_login_password(self, text_button):
        login, password = self.get_fields_login_password()

        if login == '' or login.isspace():
            self.notify(
                title=self.data.string_lang_title,
                message=self.data.string_lang_field_login_empty,
                app_icon='%s/data/images/vk_logo_red.png' % self.directory,
            )
            return
        if password == '' or password.isspace():
            self.notify(
                title=self.data.string_lang_title,
                message=self.data.string_lang_field_password_empty,
                app_icon='%s/data/images/vk_logo_red.png' % self.directory,
            )
            return

        self.input_dialog.dismiss()
        self.save_login_password(login, password)

    def save_login_password(self, login, password):
        # TODO: Сохранить access_token и зашифровать его.
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

        self.screen.ids.load_screen.ids.status.text = \
            self.data.string_lang_authorization
        Clock.schedule_once(_authorization_on_vk, 1)

    def authorization_on_vk(self, login, password):
        result, text_error = vkr.log_in(login=login, password=password)

        if not result:
            self.set_dialog_on_fail_authorization()
            self.open_dialog(
                text=self.data.string_lang_error_auth.format(text_error),
                dismiss=True
            )
        else:
            self.config.set('General', 'authorization', 1)
            self.config.write()

            if not os.path.exists(self.path_to_avatar):
                self.load_avatar()
            if self.data.user_name == 'User':
                self.set_user_name()

            self.set_issues_in_group()
            self.set_info_for_group()

            self.screen.ids.manager.current = 'previous'

    def load_avatar(self):
            self.screen.ids.load_screen.ids.status.text = \
                self.data.string_lang_load_avatar
            avatar, text_error = vkr.get_user_photo(size='max')

            if avatar:
                path_to_avatar_origin = \
                    self.directory + '/data/images/avatar_origin.png'
                path_to_avatar_portrait = self.path_to_avatar
                with open(path_to_avatar_origin, 'wb') as avatar_origin:
                    avatar_origin.write(avatar)

                create_previous_portrait(
                    path_to_avatar_origin, path_to_avatar_portrait
                )
                os.remove(path_to_avatar_origin)
                Clock.schedule_once(lambda x: self.set_avatar(
                    path_to_avatar_portrait), 1)

    def set_info_for_group(self):
        self.screen.ids.load_screen.ids.status.text = \
                self.data.string_lang_get_info_for_group
        self.group_info, text_error = vkr.get_info_from_group()

    def set_user_name(self):
        self.screen.ids.load_screen.ids.status.text = \
            self.data.string_lang_load_user_name
        name, info = vkr.get_user_name()

        if name:
            self.config.set('General', 'user_name', name)
            self.config.write()
            self.nav_drawer.ids.user_name.text = name

    def set_issues_in_group(self):
        self.screen.ids.load_screen.ids.status.text = \
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
            self.data.issues_in_group = issues_in_group
            self.nav_drawer.ids.issues_in_group.text = \
                self.data.string_lang_issues_in_group.format(
                    str(issues_in_group)
                )
