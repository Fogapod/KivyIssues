# -*- coding: utf-8 -*-

import os
import threading
import time

from kivy.clock import Clock

from libs.createpreviousportrait import create_previous_portrait
from libs import vkrequests as vk_requests

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
        Clock.schedule_once(self.show_progress_authorization, 0)
        thread_authorization = threading.Thread(
            target=self.authorization_on_vk,
            args=(self.login, self.password,)
        )
        thread_authorization.start()

    def authorization_on_vk(self, login, password):
        result, info = vk_requests.log_in(login, password)

        if not result:
            self.dialog_authorization.dismiss()
            self.open_dialog(
                text=self.data.string_lang_error_auth.format(info),
                dismiss=True
            )
            self.screen.ids.previous.ids.button_question.bind(
                on_release=lambda x: snackbar.make(
                    self.data.string_lang_please_authorization)
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
            avatar, info = vk_requests.get_user_photo('photo_max')

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
        name, info = vk_requests.get_user_name()

        if name:
            self.config.set('General', 'user_name', name)
            self.config.write()
            self.nav_drawer.ids.user_name.text = name

    def set_issues_in_group(self):
        self.instance_text_authorization.text = \
            self.data.string_lang_load_issues_in_group
        issues_in_group, info = vk_requests.get_issue_count()

        if issues_in_group:
            self.config.set('General', 'issues_in_group', issues_in_group)
            self.config.write()
            self.nav_drawer.ids.issues_in_group.text = str(issues_in_group)

    def test(self):
            wall_posts, info = vk_requests.get_issues('0', '1')

            profile_dict = wall_posts['profiles'][0]
            items_dict =  wall_posts['items'][0]
            attachments_dict = items_dict['attachments'][0]

            avatar_author = profile_dict['photo_50']
            first_name = profile_dict['first_name']
            last_name = profile_dict['last_name']
            name_author = '{} {}'.format(first_name, last_name)
            date_post = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                    items_dict['date']
                )
            )
            text_post = items_dict['text']
            int_comments_on_post = items_dict['comments']['count']

            if 'attachments' in items_dict:
                title_attachments = attachments_dict['link']['title']
                url_attachments = attachments_dict['link']['url']
                url_caption = attachments_dict['link']['caption']
                photo_attachments = \
                    attachments_dict['link']['photo']['photo_130']
