# -*- coding: utf-8 -*-

import os
import sys


from kivy.app import App
# from kivy.animation import Animation
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ObjectProperty

from libs import programdata as data
from libs import programclass as _class
from libs.programclass.showposts import ShowPosts
from libs.createpreviousportrait import create_previous_portrait
from libs.uix.lists import Lists
from libs.uix.dialogs import dialog, file_dialog, dialog_progress,\
    input_dialog, card

# Базовые классы Activity.
from libs.uix.kv.activity.baseclass.startscreen import StartScreen
from libs.uix.kv.activity.baseclass.post import Post
from libs.uix.kv.activity.baseclass.boxposts import BoxPosts
from libs.uix.kv.activity.baseclass.form_input_text import FormInputText
from libs.uix.kv.activity.baseclass.scrmanager import ScrManager
from libs.uix.kv.activity.baseclass.selection import Selection
from libs.uix.kv.activity.baseclass.loadscreen import LoadScreen
from libs.uix.kv.activity.baseclass.draweritem import DrawerItem
from libs.uix.kv.activity.baseclass.previous import Previous

from kivymd.theming import ThemeManager
from kivymd.navigationdrawer import NavigationDrawer
from kivymd.bottomsheet import MDGridBottomSheet, GridBSItem

from plyer import notification


class GridBottomSheet(MDGridBottomSheet):

    # Переопределил метод, поскольку в оригинале item просто биндился
    # на закрытие меню - item.bind(on_release=lambda x: self.dismiss()),
    # не вызывая переданную ему функцию.
    # TODO: в примере kitchen_sink.py KivyMD callback вызывается успешно -
    # пересмотреть свой код.
    def add_item(self, text, callback, icon_src):
        item = GridBSItem(
            caption=text,
            on_release=callback,
            source=icon_src
        )
        item.bind(on_release=callback)
        if self.gl_content.children.__len__() % 3 == 0:
            self.gl_content.height += dp(96)
        self.gl_content.add_widget(item)


class NavDrawer(NavigationDrawer):
    _app = ObjectProperty()

    def show_posts(self, count_issues=None, only_questions=True):
        '''Вызывает функцию, выводящую Activity с постами группы.

        :param only_questions: все или только свои посты;
        :param count_issues: количество постов, str;

        '''

        def _show_posts(interval):
            if not count_issues:
                issues = str(self._app.data.issues_in_group)
            else:
                if count_issues == '0':
                    return
                else:
                    issues = count_issues

            ShowPosts(
                app=self._app, count_issues_comments=issues,
                only_questions=only_questions
            ).show_posts()

        self.toggle()
        Clock.schedule_once(_show_posts, .3)


class Program(App, _class.ShowPlugin, _class.ShowAbout, _class.ShowLicense,
              _class.AuthorizationOnVK, _class.GetAndSaveLoginPassword,
              _class.WorkWithPosts):
    '''Функционал программы.'''

    title = data.string_lang_title
    icon = 'data/images/kivy_logo.png'
    nav_drawer = ObjectProperty()
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'BlueGrey'

    def __init__(self, **kvargs):
        super(Program, self).__init__(**kvargs)
        Window.bind(on_keyboard=self.events_program)

        self.data = data
        self.window = Window
        self.Post = Post
        self.BoxPosts = BoxPosts
        self.show_posts = None
        self.instance_dialog = None
        self.dialog_progress = None
        self.user_choice = False
        self.group_info = None
        self.login = data.regdata['login']
        self.password = data.regdata['password']
        self.path_to_avatar = self.directory + '/data/images/avatar.png'
        self.load_all_kv_files(self.directory + '/libs/uix/kv')
        self.load_all_kv_files(self.directory + '/libs/uix/kv/activity')
        self.bottom_sheet = GridBottomSheet()
        self.config = ConfigParser()
        self.config.read(data.prog_path + '/program.ini')
        self.screen = StartScreen()  # главный экран программы
        self.manager = self.screen.ids.manager
        self.nav_drawer = NavDrawer(title=data.string_lang_menu)

    def get_application_config(self):
        return super(Program, self).get_application_config(
                        '{}/%(appname)s.ini'.format(self.directory))

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'language', 'Русский')
        config.setdefault('General', 'theme', 'default')
        config.setdefault('General', 'authorization', 0)
        config.setdefault('General', 'issues_in_group', 0)
        config.setdefault('General', 'count_issues', 20)
        config.setdefault('General', 'user_name', 'User')
        config.setdefault(
            'General', 'regdata', "{'login': None, 'password': None}"
        )

    def build(self):
        # Пункт меню 'Авторизация'.
        self.bottom_sheet.add_item(
            data.string_lang_authorization[:-3],
            lambda x: self.authorization_from_button_sheet(),
            'data/images/auth.png'
        )

        if not self.login or not self.password:
            Clock.schedule_once(self.show_dialog_registration, 1)
        else:  # авторизация на сервере
            self._authorization_on_vk(self.login, self.password)

        Clock.schedule_interval(self.check_info_group, 1)

        return self.screen

    def check_info_group(self, interval):
        '''Устанавливает значения переменных для экрана Previous.'''

        if self.group_info:
            screen_previous = self.screen.ids.previous

            screen_previous.ids.group_title.source = \
                self.group_info['photo_200']
            screen_previous.ids.group_name.text = \
                '[size=14][b]%s[/b][/size]\n[size=11]%s[/size]' % (
                    self.group_info['name'], self.group_info['status']
                )
            screen_previous.ids.group_link.text = \
                '[ref={link}]{link}[/ref]'.format(
                    link='https://vk.com/%s' % self.group_info['screen_name']
                )
            screen_previous.ids.group_people.text = \
                '%s %s' % (
                    data.string_lang_people, self.group_info['members_count']
                )
            screen_previous.ids.description.text = \
                self.group_info['description']
            screen_previous.ids.input_text_form.ids.text_input.message = \
                data.string_lang_ask_a_question

            Clock.unschedule(self.check_info_group)

    def authorization_from_button_sheet(self):
        '''Выводит список с пунктами 'Текущий пароль/Новый пароль' при
        выборе пункта меню "Авторизация".'''

        def callback(text_item):
            dialog.dismiss()

            if text_item == data.string_lang_current_password:
                self._authorization_on_vk(self.login, self.password)
            elif text_item == data.string_lang_new_password:
                Clock.schedule_once(self.show_dialog_registration, 0)

        self.bottom_sheet.dismiss()
        current_or_new_password_list = Lists(
            list_items=data.menu_items, events_callback=callback,
            flag='single_list'
        )
        dialog = card(current_or_new_password_list)

    def show_login_and_password(self, instance_selection):
        '''
        Устанавливает свойства текстовых полей для ввода логина и пароля.

        :type instance_selection: <class 'kivy.weakproxy.WeakProxy'>;
        :param instance_selection:
            <libs.uix.kv.activity.baseclass.selection.Selection>

        '''

        if instance_selection.ids.check.active:
            self.input_dialog.ids.login.password = False
            self.input_dialog.ids.password.password = False
        else:
            self.input_dialog.ids.login.password = True
            self.input_dialog.ids.password.password = True

    def show_dialog_registration(self, interval):
        '''Окно с формой регистрации.'''

        self.input_dialog = input_dialog(
            title=self.data.string_lang_registration,
            hint_text_login='Login', password=True, dismiss=False,
            hint_text_password='Password', text_button_ok='OK',
            events_callback=self.check_fields_login_password,
            text_color=self.theme_cls.primary_color
        )

    def show_progress(self, interval=0, text='Wait', func_dismiss=None):
        '''Прогресс загрузки данных с сервера.'''

        def p():
            pass

        if not func_dismiss:
            func_dismiss = p

        self.dialog_progress, self.instance_text_progress = \
            dialog_progress(
                text_wait=text, text_color=self.data.text_color_from_hex,
                events_callback=lambda x: func_dismiss()
            )

    def show_input_form(self, instance):
        '''Выводит окно формы для ввода текста.'''

        # FIXME: не работает анимация.
        # animation = Animation()
        # animation += Animation(d=.5, y=0, t='out_cubic')
        # animation.start(instance)

        instance.pos_hint = {'y': 0}

    def hide_input_form(self, instance):
        '''Скрывает окно формы для ввода текста.'''

        instance.pos_hint = {'y': -.3}

    def set_dialog_on_fail_authorization(self):
        '''Диалоговое окно с просьбой авторзироваться.'''

        # TODO: Добавить прерывание запроса данных с сервера.
        self.dialog_progress.dismiss()
        self.screen.ids.previous.ids.button_question.bind(
            on_release=lambda *args: self.notify(
                title=data.string_lang_title,
                message=data.string_lang_please_authorization,
                app_icon='%s/data/images/vk_logo_red.png' % self.directory,
            )
        )

    def check_file_is(self, path_to_file, check_image=False):
        '''Проверяет корректность прикрепляемых файлов по расширению.'''

        if check_image:
            possible_files_ext = \
                data.possible_files[data.string_lang_add_image][0]
        else:
            possible_files_ext = \
                data.possible_files[data.string_lang_add_file][0]

        if os.path.splitext(path_to_file)[1] in possible_files_ext:
            return True

        return False

    def add_content(self, instance_selection):
        '''Выводит файловый менеджер для выбора файлов, которые будут
        прикреплены к отправляемому сообщению.

        :param instance_selection:
            <libs.uix.kv.activity.baseclass.selection.Selection>;
        :param instance_selection:
            <class 'kivy.weakproxy.WeakProxy'>;

        '''

        def dialog_dismiss():
            if not self.user_choice:
                instance_selection.ids.check.active = False
            else:
                self.user_choice = False

        def select_file(path_to_file):
            self.user_choice = True
            dialog_manager.dismiss()
            name_check = instance_selection.ids.label.text
            self.path_to_file, name_file = os.path.split(path_to_file)

            if self.check_file_is(path_to_file) or \
                    self.check_file_is(path_to_file, check_image=True):
                instance_selection.ids.label.text = name_file
            else:
                if os.path.splitext(name_file) in \
                        data.possible_files[data.string_lang_add_file][0]:
                    icon = '%s/data/images/paperclip_red.png' % self.directory
                else:
                    icon = '%s/data/images/camera_red.png' % self.directory

                self.notify(
                    title=self._app.data.string_lang_title,
                    message=data.possible_files[name_check][1], app_icon=icon
                )
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
                    self.directory + '/data/images/avatar.png'
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
            self.show_bottom_sheet()
            # self.nav_drawer.toggle()

        return True

    def back_screen(self, name_screen):
        '''Менеджер экранов. Вызывается при нажатии Back Key
        и шеврона "Назад" в ToolBar.

        :type name_screen: str;
        :param name_screen: имя Activity, которое будет установлено;

        '''
        print(name_screen)
        print(self.manager.screens)

        name_current_screen = self.manager.current
        if name_current_screen == 'ask a question' and self.fill_out_form:
            self.dialog_fill_out_form()
            return

        # Нажата BackKey.
        if name_screen in (1001, 27):
            if name_current_screen == 'previous':
                self.dialog_exit()
                return

        if name_current_screen == 'ask a question' \
                or name_screen in (1001, 27):
            self.manager.current = 'previous'
        elif name_current_screen == 'box posts' \
                or name_screen in (1001, 27):
            if name_screen in (1001, 27):
                self.manager.current = self.screen.ids.box_posts.old_screen
            else:
                self.manager.current = name_screen
        else:
            self.manager.current = name_screen

    def dialog_exit(self, *args):
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
            self.close_dialog()
            return

        self.instance_dialog = dialog(
            text=text, title=title, dismiss=dismiss, buttons=buttons
        )

    def notify(self, title='Title:', message='Message!',
               app_icon='data/logo/kivy-icon-128.png', timeout=1):
        notification.notify(
            title=title, message=message, app_icon=app_icon, timeout=timeout
        )

    def load_all_kv_files(self, directory_kv_files):
        for kv_file in os.listdir(directory_kv_files):
            if kv_file in ('bugreporter.kv', '__init__.py', '__init__.pyo',
                           '__init__.pyc') or \
                    os.path.isdir(directory_kv_files + '/' + kv_file):
                continue
            Builder.load_file(directory_kv_files + '/' + kv_file)

    def show_bottom_sheet(self):
        self.bottom_sheet.open()

    def on_config_change(self, config, section, key, value):
        '''Вызывается при выборе одного из пунктов настроек программы.'''

        if key == 'language':
            if not os.path.exists('%s/data/language/%s.txt' %(
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
        '''Ставит приложение на 'паузу' при выходе из него.
        В противном случае запускает программу заново.'''

        return True
