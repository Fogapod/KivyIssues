# -*- coding: utf-8 -*-

import os
import sys
from random import choice

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.clock import Clock
from kivy.properties import ObjectProperty

from libs import programdata as data
from libs import programclass as _class
from libs.createpreviousportrait import create_previous_portrait
from libs.uix.dialogs import dialog, file_dialog, dialog_progress, input_dialog
from libs.uix.kv.activity.baseclass.startscreen import StartScreen
from libs.uix.kv.activity.baseclass.scrmanager import ScrManager
from libs.uix.kv.activity.baseclass.selection import Selection
from libs.uix.kv.activity.baseclass.draweritem import DrawerItem
from libs.uix.kv.activity.baseclass.askaquestion import AskAQuestion
from libs.uix.kv.activity.baseclass.previous import Previous

from kivymd import snackbar
from kivymd.theming import ThemeManager
from kivymd.navigationdrawer import NavigationDrawer


in_development_msg = '''


#############################################
#                                           #
# The project is still in development ...   #
#                                           #
#############################################
'''


class InDevelopment(Exception):
    pass


class NavDrawer(NavigationDrawer):
    pass


class Program(App, _class.ShowPlugin, _class.ShowAbout, _class.ShowLicense,
              _class.IssueForm, _class.AuthorizationOnVK,
              _class.GetAndSaveLoginPassword):
    '''Функционал программы.'''

    # raise InDevelopment(in_development_msg)

    title = data.string_lang_title
    icon = 'data/images/logo.png'
    nav_drawer = ObjectProperty()
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'BlueGrey'

    def __init__(self, **kvargs):
        super(Program, self).__init__(**kvargs)
        Window.bind(on_keyboard=self.events_program)

        self.data = data
        self.window = Window
        self.instance_dialog = None
        self.fill_out_form = None
        self.dialog_authorization = None
        self.set_default_text_check = True
        self.open_filemanager_on_check = True
        self.user_choice = False
        self.login = data.regdata['login']
        self.password = data.regdata['password']
        self.load_all_kv_files('{}/libs/uix/kv'.format(self.directory))
        self.load_all_kv_files(
            '{}/libs/uix/kv/activity'.format(self.directory)
        )
        self.config = ConfigParser()
        self.config.read('{}/program.ini'.format(data.prog_path))
        self.check_existence_issues()
        self.saved_form = self.read_form()
        # Главный экран программы.
        self.screen = StartScreen()
        self.manager = self.screen.ids.manager
        self.nav_drawer = NavDrawer(title=data.string_lang_menu)

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'language', 'Русский')
        config.setdefault('General', 'theme', 'default')
        config.setdefault('General', 'authorization', 0)
        config.setdefault('General', 'issues_in_group', 0)
        config.setdefault('General', 'user_name', 'User')
        config.setdefault(
            'General', 'regdata', "{'login': None, 'password': None}"
        )

    def build(self):
        Clock.schedule_interval(self.set_banner, 8)

        if not self.login or not self.password:
            Clock.schedule_once(self.show_dialog_registration, 3)
        else:  # авторизация на сервере
            self._authorization_on_vk(self.login, self.password)
        if self.saved_form:
            Clock.schedule_once(self.dialog_restore_form, 3)

        return self.screen

    def show_login_and_password(self, instance_selection):
        if instance_selection.ids.check.active:
            self.input_dialog.ids.login.password = False
            self.input_dialog.ids.password.password = False
        else:
            self.input_dialog.ids.login.password = True
            self.input_dialog.ids.password.password = True

    def show_dialog_registration(self, interval):
        self.input_dialog = input_dialog(
            title=self.data.string_lang_registration,
            hint_text_login='Login', password=True, dismiss=False,
            hint_text_password='Password', text_button_ok='OK',
            events_callback=self.check_fields_login_password,
            text_color=self.theme_cls.primary_color
        )

    def show_progress_authorization(self, interval):
        self.dialog_authorization, self.instance_text_authorization = \
            dialog_progress(
                text_wait=self.data.string_lang_authorization,
                text_color=self.data.text_color_from_hex,
                events_callback=lambda x: self.dialog_authorization.dismiss()
            )

    def dialog_not_authorization(self, *args):
        self.open_dialog(
            text=self.data.string_lang_please_authorization, dismiss=True
        )

    def dialog_restore_form(self, interval):
        def restore_form():
            self.manager.current = 'ask a question'
            self.set_default_text_check = False
            self.open_filemanager_on_check = False
            self.restore_form()
            self.close_dialog()
            self.open_filemanager_on_check = True

        def clear_data():
            self.clear_data()
            self.close_dialog()

        self.open_dialog(
            text=data.string_lang_old_form_exists, dismiss=True,
            buttons=[
                [data.string_lang_yes, lambda *x: restore_form()],
                [data.string_lang_no, lambda *x: self.close_dialog()],
                [data.string_lang_clear_data, lambda *x: clear_data()]
            ]
        )

    def check_new_issues(self):
        '''Возвращает значение 'comment-outline', если в группе нет новых
        вопросов, и 'comment-text', если есть.'''

        def get_new_issues():
            '''get запрос'''

        return 'comment-text' if get_new_issues() else 'comment-outline'

    def set_banner(self, td):
        try:
            instance_banner = \
                self.screen.ids.manager.current_screen.ids.banner.canvas.children[1]
            name_banner = choice(data.name_banners)
            instance_banner.source = 'data/images/banners/{}'.format(
               name_banner
            )
        except AttributeError:
            pass

    def check_file_is(self, path_to_file, check_image=False):
        if check_image:
            possible_files_ext = data.possible_files[
                data.string_lang_add_image][0]
        else:
            possible_files_ext = data.possible_files[
                data.string_lang_add_file][0]

        if os.path.splitext(path_to_file)[1] in possible_files_ext:
            return True
        return False

    def check_status(self, instance_selection):
        if self.open_filemanager_on_check:
            if instance_selection.ids.check.active:
                self.add_content(instance_selection)
            else:
                label_text = instance_selection.ids.label.text
                if label_text not in (
                        self.data.string_lang_add_image,
                        self.data.string_lang_add_file):
                    if self.check_file_is(label_text):
                        instance_selection.ids.label.text = \
                            self.data.string_lang_add_file
                    else:
                        instance_selection.ids.label.text = \
                            self.data.string_lang_add_image

    def add_content(self, instance_selection):
        '''Выводит файловый менеджер для выбора файлов, которые будут
        прикреплены к отправляемому сообщению.'''

        def dialog_dismiss():
            if not self.user_choice:
                instance_selection.ids.check.active = False
            else:
                self.user_choice = False

        def select_file(path_to_file):
            self.user_choice = True
            dialog_manager.dismiss()
            name_check = instance_selection.ids.label.text

            if self.check_file_is(path_to_file) or \
                    self.check_file_is(path_to_file, check_image=True):
                self.path_to_file, name_file = os.path.split(path_to_file)
                instance_selection.ids.label.text = name_file
            else:
                snackbar.make(self.data.possible_files[name_check][1])
                instance_selection.ids.check.active = False

        dialog_manager, file_manager = file_dialog(
            title='Choice', path='.', filter='files',
            events_callback=select_file
        )
        dialog_manager.on_dismiss = dialog_dismiss

    def set_avatar(self, path_to_avatar):
        self.nav_drawer.ids.avatar.source = path_to_avatar
        self.nav_drawer.ids.avatar.reload()

    def choice_avatar_user(self):
        '''Выводит файловый менеджер для выбора аватара
        и устанавливает его в качестве аватара пользователя.'''

        def on_select(path_to_avatar):
            dialog_manager.dismiss()
            if self.check_file_is(path_to_avatar, check_image=True):
                new_path_to_avatar = \
                    '{}/data/images/avatar.png'.format(self.directory)
                create_previous_portrait(path_to_avatar, new_path_to_avatar)
                self.set_avatar(new_path_to_avatar)
            else:
                dialog(
                    title=self.title, text=self.data.string_lang_wrong_image
                )

        dialog_manager, file_manager = file_dialog(
            title=self.data.string_lang_select_avatar, path='.',
            filter='files', events_callback=on_select
        )

    def events_program(self, instance, keyboard, keycode, text, modifiers):
        '''Вызывается при нажатии кнопки Меню или Back Key
        на мобильном устройстве.'''

        if keyboard in (1001, 27):
            if self.nav_drawer._open:
                self.nav_drawer.toggle()
            self.back_screen(keyboard)
        elif keyboard in (282, 319):
            self.nav_drawer.toggle()

        return True

    def back_screen(self, name_screen):
        '''Менеджер экранов.'''

        name_current_screen = self.manager.current
        if name_current_screen == 'ask a question' and self.fill_out_form:
            self.dialog_fill_out_form()
            return

        # Нажата BackKey.
        if name_screen in (1001, 27):
            if name_current_screen == 'previous':
                self.dialog_exit()
                return

        self.manager.current = 'previous' \
            if name_current_screen == 'ask a question' \
            else name_screen

    def dialog_fill_out_form(self):
        _data = self.create_data_from_form()
        self.open_dialog(
            text=data.string_lang_fill_out_form,
            buttons=[
                [data.string_lang_yes, lambda *x: self._save_data_from_form(_data)],
                [data.string_lang_no, lambda *x: self._close_dialog()]
            ]
        )

    def dialog_exit(self):
        self.open_dialog(
            text=data.string_lang_exit,
            buttons=[
                [data.string_lang_yes, lambda *x: sys.exit(0)],
                [data.string_lang_no, lambda *x: self.close_dialog()]
            ]
        )

    def close_dialog(self):
        self.instance_dialog.dismiss()
        self.instance_dialog = None

    def open_dialog(self, text='', title=title, dismiss=False, buttons=None):
        if not buttons:
            buttons = []
        if self.instance_dialog:
            return

        self.instance_dialog = dialog(
            text=text, title=title, dismiss=dismiss, buttons=buttons
        )

    def load_all_kv_files(self, directory_kv_files):
        for kv_file in os.listdir(directory_kv_files):
            if kv_file in ('bugreporter.kv', '__init__.py', '__init__.pyo',
                           '__init__.pyc') or \
                    os.path.isdir('{}/{}'.format(
                        directory_kv_files, kv_file)):
                continue
            Builder.load_file('{}/{}'.format(directory_kv_files, kv_file))

    def on_config_change(self, config, section, key, value):
        '''Вызывается при выборе одного из пункта настроек программы.'''

        if key == 'language':
            if not os.path.exists('{}/data/language/{}.txt'.format(
                    self.directory, data.select_locale[value])):
                dialog(
                    text=data.string_lang_not_locale.format(
                        data.select_locale[value]),
                    title=self.title
                )
                config.set(section, key, data.old_language)
                config.write()
                self.close_settings()

    def on_pause(self):
        '''Ставит приложение на 'паузу' при выхоже из него.
        В противном случае запускает программу заново'''

        return True

    def _close_dialog(self, clear_form=True):
        self.close_dialog()
        if clear_form:
            if self.manager.current == 'ask a question':
                self.clear_form()
                self.fill_out_form = None
        if self.manager.current == 'ask a question':
            self.manager.current = 'previous'

    def _save_data_from_form(self, data):
        self.save_form(data=data)
        self._close_dialog(clear_form=False)
