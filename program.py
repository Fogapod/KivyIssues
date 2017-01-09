# -*- coding: utf-8 -*-

import os
import sys

from kivy.app import App
# from kivy.animation import Animation
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.clock import Clock
from kivy.properties import ObjectProperty

from libs import programdata as data
from libs.programdata import thread
from libs import programclass as _class
from libs.programclass.showposts import ShowPosts
from libs.createpreviousportrait import create_previous_portrait
from libs.uix.dialogs import dialog, file_dialog, dialog_progress

# Базовые классы Activity.
from libs.uix.kv.activity.baseclass.startscreen import StartScreen
from libs.uix.kv.activity.baseclass.post import Post
from libs.uix.kv.activity.baseclass.boxposts import BoxPosts
from libs.uix.kv.activity.baseclass.license import ShowLicense
from libs.uix.kv.activity.baseclass.form_input_text import FormInputText
from libs.uix.kv.activity.baseclass.passwordform import PasswordForm
from libs.uix.kv.activity.baseclass.selection import Selection
from libs.uix.kv.activity.baseclass.loadscreen import LoadScreen
from libs.uix.kv.activity.baseclass.previous import Previous

from libs.vkrequests import create_issue, create_comment

from kivymd.theming import ThemeManager
from kivymd.navigationdrawer import NavigationDrawer

from plyer import notification


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

        self._toggle()
        Clock.schedule_once(_show_posts, .3)

    def _toggle(self):
        if self._app.manager.current == 'load screen':
            return
        self.toggle()


class Program(App, _class.ShowPlugin, _class.ShowAbout, _class.WorkWithPosts,
              _class.AuthorizationOnVK, _class.GetAndSaveLoginPassword):
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
        self.show_license = ShowLicense(_app=self).show_license
        self.show_posts = None
        self.instance_dialog = None
        self.password_form = None
        self.dialog_progress = None
        self.attach_file = None
        self.attach_image = None
        self.group_info = None
        self.result_sending_comment_issues = None
        self.path_to_attach_file = None
        self.login = data.regdata['login']
        self.password = data.regdata['password']
        self.path_to_avatar = self.directory + '/data/images/avatar.png'
        self.load_all_kv_files(self.directory + '/libs/uix/kv')
        self.load_all_kv_files(self.directory + '/libs/uix/kv/activity')
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
        if not self.login or not self.password:
            self.show_screen_registration()
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

    def show_login_and_password(self, instance_selection):
        '''
        Устанавливает свойства текстовых полей для ввода логина и пароля.

        :type instance_selection: <class 'kivy.weakproxy.WeakProxy'>;
        :param instance_selection:
            <libs.uix.kv.activity.baseclass.selection.Selection>

        '''

        if instance_selection.ids.check.active:
            self.password_form.ids.login.password = False
            self.password_form.ids.password.password = False
        else:
            self.password_form.ids.login.password = True
            self.password_form.ids.password.password = True

    def show_screen_registration(self, fail_registration=False):
        '''Окно с формой регистрации.'''

        if not self.password_form:
            self.password_form = \
                PasswordForm(callback=self.check_fields_login_password)

        self.screen.ids.load_screen.add_widget(self.password_form)

        # Если произошла ошибка регистрации, деактивируем спиннер и чистим
        # лейблы статуса авторизации.
        if fail_registration:
            self.screen.ids.load_screen.ids.spinner.active = False
            self.screen.ids.load_screen.ids.status.text = ''

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

    def callback_for_input_text(self, *args):
        '''Вызывается при событиях из формы ввода текста.

        :args:
            flag: ('SEND',),
            post_id: '725',
            reply_to: '',
            input_text_form:
                <libs.uix.kv.activity.baseclass.form_input_text.FormInputText>,
            post_instance: <libs.uix.kv.activity.baseclass.post.Post>

            '''

        @thread
        def _create_issues():
            self.result_sending_comment_issues, text_error = create_issue(
                {'file': self.attach_file,
                 'image': self.attach_image,
                 'issue': text_from_form,
                 'theme': ''}
            )

        @thread
        def _create_comment():
            self.result_sending_comment_issues, text_error = create_comment(
                {'file': self.attach_file,
                 'image': self.attach_image,
                 'text': text_from_form},
                post_id=args[1], reply_to=args[2]
            )

        def check_result_sending_comment_issues(interval):
            def unschedule():
                Clock.unschedule(check_result_sending_comment_issues)
                self.result_sending_comment_issues = None
                self.notify(
                    title=data.string_lang_title, message=message,
                    app_icon=icon
                )

            message = data.string_lang_sending
            icon = '%s/data/images/send.png' % self.directory

            if self.result_sending_comment_issues:
                if current_screen != 'previous':
                    post_instance = args[4]
                    post_instance.update_post(
                        text_from_form, args[1], args[2]
                    )
                unschedule()
            elif self.result_sending_comment_issues is False:
                message = data.string_lang_sending_error
                icon = '%s/data/images/error.png' % self.directory
                unschedule()

        current_screen = self.screen.ids.manager.current
        # flag - 'FILE', 'FOTO', 'SEND'
        if current_screen == 'previous':  # форма из главного экрана
            flag = args[0]
        else:  # форма из списка комментариев
            flag = args[0][0]

        if flag in ('FILE', 'FOTO'):
            self.add_content(flag)
        elif flag == 'SEND':
            if current_screen == 'previous':
                input_text_form = \
                    self.screen.ids.previous.ids.input_text_form
                text_from_form = input_text_form.ids.text_input.text
            else:
                input_text_form = args[3]
                self.hide_input_form(input_text_form)
                text_from_form = input_text_form.ids.text_input.text

            if text_from_form.isspace() or text_from_form != '':

                if current_screen == 'previous':
                    _create_issues()  # отправка вопроса
                else:
                    _create_comment()  # отправка комментария

                input_text_form.clear()
                Clock.schedule_interval(
                    check_result_sending_comment_issues, 0
                )

    def add_content(self, flag):
        '''Выводит файловый менеджер для выбора файлов'''

        def select_file(path_to_file):
            dialog_manager.dismiss()
            path_to_attach_file, name_file = os.path.split(path_to_file)

            if os.path.splitext(name_file)[1] not in data.possible_files:
                if flag == 'FILE':
                    icon = \
                        '%s/data/images/paperclip_red.png' % self.directory
                    message = data.string_lang_wrong_file
                else:
                    icon = '%s/data/images/camera_red.png' % self.directory
                    message = data.string_lang_wrong_image

                self.notify(
                    title=data.string_lang_title, message=message,
                    app_icon=icon
                )
            # TODO: добавить визуализацию прикрепленных файлов.
            else:
                if flag == 'FILE':
                    self.attach_file = path_to_file
                else:
                    self.attach_image = path_to_file

                input_text_form = \
                    self.screen.ids.previous.ids.input_text_form
                text = input_text_form.ids.text_input.text
                input_text_form.ids.text_input.text = \
                    '%s\n[#Прикрепленный файл - %s]' % (text, name_file)

        dialog_manager, file_manager = file_dialog(
            title='Choice', path='.', filter='files',
            size=(.9, .9), events_callback=select_file
        )

    def set_avatar(self, path_to_avatar):
        self.nav_drawer.ids.avatar.source = path_to_avatar
        self.nav_drawer.ids.avatar.reload()

    def choice_avatar_user(self):
        '''Выводит файловый менеджер для выбора аватара
        и устанавливает его в качестве аватара пользователя.'''

        def on_select(path_to_avatar):
            dialog_manager.dismiss()

            if os.path.splitext(path_to_avatar)[1] \
                    not in data.possible_files[:3]:
                self.notify(
                    title=data.string_lang_title,
                    message=data.string_lang_wrong_image,
                    app_icon='%s/data/images/camera_red.png' % self.directory
                )
            else:
                new_path_to_avatar = \
                    self.directory + '/data/images/avatar.png'
                create_previous_portrait(path_to_avatar, new_path_to_avatar)
                self.set_avatar(new_path_to_avatar)

        dialog_manager, file_manager = file_dialog(
            title=self.data.string_lang_select_avatar, path='.',
            filter='files', events_callback=on_select, size=(.9, .9)
        )

    def events_program(self, instance, keyboard, keycode, text, modifiers):
        '''Вызывается при нажатии кнопки Меню или Back Key
        на мобильном устройстве.'''

        if keyboard in (1001, 27):
            if self.nav_drawer._open:
                self.nav_drawer.toggle()
            self.back_screen(keyboard)
        elif keyboard in (282, 319):
            pass

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

        # Нажата BackKey.
        if name_screen in (1001, 27):
            if name_current_screen == 'previous':
                self.dialog_exit()
                return

        if name_current_screen == 'box posts' \
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
