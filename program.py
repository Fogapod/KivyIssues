# -*- coding: utf-8 -*-

import os
import re
import sys
import gettext
import ast
import webbrowser

from kivy.app import App
from kivy.uix.image import Image
# from kivy.animation import Animation
from kivy.lang import Builder
from kivy.lang import Observable
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty

from main import __version__
from libs._thread import thread
from libs import programclass as _class
from libs.programclass.showposts import ShowPosts
from libs.createpreviousportrait import create_previous_portrait
from libs.uix.dialogs import dialog, file_dialog, card
from libs.uix.lists import Lists

# Базовые классы Activity.
from libs.uix.kv.activity.baseclass.startscreen import StartScreen
from libs.uix.kv.activity.baseclass.post import Post
from libs.uix.kv.activity.baseclass.boxposts import BoxPosts
from libs.uix.kv.activity.baseclass.license import ShowLicense
from libs.uix.kv.activity.baseclass.passwordform import PasswordForm
from libs.uix.kv.activity.baseclass.form_input_text import FormInputText
from libs.uix.kv.activity.baseclass.selection import Selection
from libs.uix.kv.activity.baseclass.loadscreen import LoadScreen
from libs.uix.kv.activity.baseclass.previous import Previous

from libs.vkrequests import create_issue, create_comment

from kivymd.theming import ThemeManager
from kivymd.navigationdrawer import NavigationDrawer

from plyer import notification


class Translation(Observable):
    observers = []
    lang = None

    def __init__(self, defaultlang):
        super(Translation, self).__init__()

        self.ugettext = None
        self.lang = defaultlang
        self.switch_lang(self.lang)

    def _(self, text):
        try:
            return self.ugettext(text)
        except UnicodeDecodeError:
            return self.ugettext(text.decode('utf-8'))

    def fbind(self, name, func, args, **kwargs):
        if name == "_":
            self.observers.append((func, args, kwargs))
        else:
            return super(Translation, self).fbind(
                name, func, *args, **kwargs
            )

    def funbind(self, name, func, args, **kwargs):
        if name == "_":
            key = (func, args, kwargs)
            if key in self.observers:
                self.observers.remove(key)
        else:
            return super(Translation, self).funbind(
                name, func, *args, **kwargs
            )

    def switch_lang(self, lang):
        # get the right locales directory, and instanciate a gettext
        locale_dir = os.path.join(
            os.path.dirname(__file__), 'data', 'locales'
        )
        locales = \
            gettext.translation('kivyissues', locale_dir, languages=[lang])
        self.ugettext = locales.ugettext

        # update all the kv rules attached to this text
        for func, largs, kwargs in self.observers:
            func(largs, None, None)


class NavDrawer(NavigationDrawer):
    _app = ObjectProperty()

    def show_posts(self, count_issues=None, only_questions=True):
        '''Вызывает функцию, выводящую Activity с постами группы.

        :param only_questions: все или только свои посты;
        :param count_issues: количество постов, str;

        '''

        def _show_posts(interval):
            if not count_issues:
                issues = str(self._app.issues_in_group)
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


class Program(App, _class.ShowPlugin, _class.WorkWithPosts,
              _class.AuthorizationOnVK, _class.GetAndSaveLoginPassword):
    '''Функционал программы.'''

    title = 'Kivy Issues'
    icon = 'data/images/kivy_logo.png'
    nav_drawer = ObjectProperty()
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'BlueGrey'
    lang = StringProperty('ru')

    def __init__(self, **kvargs):
        super(Program, self).__init__(**kvargs)
        Window.bind(on_keyboard=self.events_program)

        self.POSSIBLE_FILES = \
            ['.png', '.jpg', '.jpeg', '.gif', '.zip', '.txt']
        self.DEVISE_ONLINE = {
            'mobile': 'data/images/mobile.png',
            'computer': 'data/images/computer.png',
            0: 'data/images/offline.png'
        }
        self.PATTERN_WHOM_COMMENT = pattern_whom_comment
        self.PATTERN_REPLACE_LINK = pattern_replace_link

        self.window = Window
        self.Post = Post
        self.BoxPosts = BoxPosts
        self.config = ConfigParser()
        self.show_posts = None
        self.instance_dialog = None
        self.password_form = None
        self.attach_file = None
        self.attach_image = None
        self.group_info = None
        self.result_sending_comment_issues = None
        self.path_to_attach_file = None
        self.path_to_avatar = self.directory + '/data/images/avatar.png'
        self.dict_language = ast.literal_eval(
            open('%s/data/locales/locales' % self.directory).read()
        )

    def get_application_config(self):
        return super(Program, self).get_application_config(
                        '{}/%(appname)s.ini'.format(self.directory))

    def build_config(self, config):
        '''Создает файл настроек приложения program.ini.'''

        config.adddefaultsection('General')
        config.setdefault('General', 'language', 'ru')
        config.setdefault('General', 'theme', 'default')
        config.setdefault('General', 'authorization', 0)
        config.setdefault('General', 'issues_in_group', 0)
        config.setdefault('General', 'count_issues', 20)
        config.setdefault('General', 'user_name', 'User')
        config.setdefault(
            'General', 'regdata', "{'login': None, 'password': None}"
        )

    def set_from_config(self):
        '''Устанавливает значения переменных из файла настроек
        program.ini.'''

        self.config.read('%s/program.ini' % self.directory)
        self.theme = self.config.get('General', 'theme')
        self.language = self.config.get('General', 'language')
        self.authorization = self.config.getint('General', 'authorization')
        self.regdata = \
            ast.literal_eval(self.config.get('General', 'regdata'))
        self.login = self.regdata['login']
        self.password = self.regdata['password']
        self.user_name = self.config.get('General', 'user_name')
        self.count_issues = self.config.getint('General', 'count_issues')
        self.issues_in_group = \
            self.config.getint('General', 'issues_in_group')

    def set_color(self):
        '''Устанавливает значение цвета для использование в .py и .kv
        файлах приложения.'''

        config_theme = ConfigParser()
        config_theme.read(
            '{}/data/themes/{theme}/{theme}.ini'.format(
                self.directory, theme=self.theme)
        )
        self.alpha = \
            get_color_from_hex(config_theme.get('color', 'alpha'))
        self.list_color = \
            get_color_from_hex(config_theme.get('color', 'list_color'))
        self.text_color_from_hex = \
            get_color_from_hex(config_theme.get('color', 'text_color'))
        self.floating_button_down_color = \
            get_color_from_hex(config_theme.get(
                'color', 'floating_button_down_color')
            )
        self.floating_button_disabled_color = \
            get_color_from_hex(config_theme.get(
                'color', 'floating_button_disabled_color')
            )

        self.text_color = config_theme.get('color', 'text_color')
        self.text_key_color = config_theme.get('color', 'text_key_color')
        self.text_link_color = config_theme.get('color', 'text_link_color')
        self.underline_rst_color = \
            config_theme.get('color', 'underline_rst_color')

    def build(self):
        self.set_from_config()
        self.set_color()
        self.translation = Translation(self.language)

        self.load_all_kv_files(self.directory + '/libs/uix/kv')
        self.load_all_kv_files(self.directory + '/libs/uix/kv/activity')
        self.screen = StartScreen()  # главный экран программы
        self.manager = self.screen.ids.manager
        self.nav_drawer = NavDrawer(title=self.translation._(u'Меню'))

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
                    self.translation._(u'Участники'),
                    self.group_info['members_count']
                )
            screen_previous.ids.description.text = \
                self.group_info['description']
            screen_previous.ids.input_text_form.ids.text_input.message = \
                self.translation._(u'Задать вопрос')

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

    def show_progress(self, screen):
        screen.add_widget(
            Image(source='data/images/waiting.gif', size_hint_y=None,
                  pos=(0, -35))
        )

    def hide_progress(self, screen):
        self.screen.ids.previous.ids.box.remove_widget(screen.children[0])

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
                    title=self.title,
                    message=message, app_icon=icon
                )

            message = self.translation._('Sent!')
            icon = '%s/data/images/send.png' % self.directory

            if self.result_sending_comment_issues:
                if current_screen != 'previous':
                    post_instance = args[4]
                    post_instance.update_post(
                        text_from_form, args[1], args[2]
                    )
                unschedule()
            elif self.result_sending_comment_issues is False:
                message = self.translation._('Error while sending!')
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

            if os.path.splitext(name_file)[1] not in self.POSSIBLE_FILES:
                if flag == 'FILE':
                    icon = \
                        '%s/data/images/paperclip_red.png' % self.directory
                    message = self.translation._('This file unsupported!')
                else:
                    icon = '%s/data/images/camera_red.png' % self.directory
                    message = self.translation._('This is not image!')

                self.notify(
                    title=self.title, message=message,
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
                    not in self.POSSIBLE_FILES[:3]:
                self.notify(
                    title=self.title,
                    message=self.translation._('This is not image!'),
                    app_icon='%s/data/images/camera_red.png' % self.directory
                )
            else:
                new_path_to_avatar = \
                    self.directory + '/data/images/avatar.png'
                create_previous_portrait(path_to_avatar, new_path_to_avatar)
                self.set_avatar(new_path_to_avatar)

        dialog_manager, file_manager = file_dialog(
            title=self.translation._(u'Выберите аватар'), path='.',
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

    def back_screen(self, event=None):
        '''Менеджер экранов. Вызывается при нажатии Back Key
        и шеврона "Назад" в ToolBar.

        :type name_screen: str;
        :param name_screen: имя Activity, которое будет установлено;

        '''

        # Нажата BackKey.
        if event in (1001, 27):
            if self.manager.current == 'previous':
                self.dialog_exit()
                return

        self.manager.current = self.manager.previous()

    def dialog_exit(self, *args):
        self.open_dialog(
            text=self.translation._(u'Закрыть приложение?'),
            buttons=[
                [self.translation._(u'Да'), lambda *x: sys.exit(0)],
                [self.translation._(u'Нет'), lambda *x: self.close_dialog()]
            ]
        )

    def show_about(self):
        def on_ref_press(instance, text_link):
            webbrowser.open(text_link)

        self.nav_drawer.toggle()
        self.screen.ids.load_screen.ids.status.text = \
            self.translation._(
                u'[size=20][b]Kivy Issues[/b][/size]\n\n'
                u'[b]Версия:[/b] {version}\n'
                u'[b]Лицензия:[/b] MIT\n\n'
                u'[size=20][b]Разработчики[/b][/size]\n\n'
                u'[b]Backend:[/b] [ref=https://m.vk.com/fogapod]'
                u'[color={link_color}]Евгений Ершов[/color][/ref]\n'
                u'[b]Frontend:[/b] [ref=https://m.vk.com/heattheatr]'
                u'[color={link_color}]Иванов Юрий[/color][/ref]\n\n'
                u'[b]Исходный код:[/b] '
                u'[ref=https://github.com/HeaTTheatR/KivyIssues]'
                u'[color={link_color}]GitHub[/color][/ref]').format(
                version=__version__,
                link_color=get_hex_from_color(self.theme_cls.primary_color)
            )
        self.screen.ids.load_screen.ids.status.bind(
            on_ref_press=on_ref_press
        )
        self.screen.ids.load_screen.ids.spinner.active = False
        self.manager.current = 'load screen'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen()]]

    def show_license(self):
        self.screen.ids.show_license.ids.text_license.text = \
                self.translation._('''
[color=78a5a3ff]Copyright (c) Easy

[color=#000]Данная лицензия разрешает лицам, получившим копию данного программного обеспечения и сопутствующей документации (в дальнейшем именуемыми [color=78a5a3ff]«Программное Обеспечение»[color=#000]), безвозмездно использовать [color=78a5a3ff]Программное Обеспечение [color=#000]без ограничений, включая неограниченное право на использование, копирование, изменение, слияние, публикацию, распространение, сублицензирование и/или продажу копий [color=78a5a3ff]Программного Обеспечения[color=#000], а также лицам, которым предоставляется данное [color=78a5a3ff]Программное Обеспечение[color=#000], при соблюдении следующих условий:

Указанное выше уведомление об авторском праве и данные условия должны быть включены во все копии или значимые части данного [color=78a5a3ff]Программного Обеспечения.

[color=78a5a3ff]ДАННОЕ ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ПРЕДОСТАВЛЯЕТСЯ «КАК ЕСТЬ», БЕЗ КАКИХ-ЛИБО ГАРАНТИЙ, ЯВНО ВЫРАЖЕННЫХ ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ ГАРАНТИИ ТОВАРНОЙ ПРИГОДНОСТИ, СООТВЕТСТВИЯ ПО ЕГО КОНКРЕТНОМУ НАЗНАЧЕНИЮ И ОТСУТСТВИЯ НАРУШЕНИЙ, НО НЕ ОГРАНИЧИВАЯСЬ ИМИ. НИ В КАКОМ СЛУЧАЕ АВТОРЫ ИЛИ ПРАВООБЛАДАТЕЛИ НЕ НЕСУТ ОТВЕТСТВЕННОСТИ ПО КАКИМ-ЛИБО ИСКАМ, ЗА УЩЕРБ ИЛИ ПО ИНЫМ ТРЕБОВАНИЯМ, В ТОМ ЧИСЛЕ, ПРИ ДЕЙСТВИИ КОНТРАКТА, ДЕЛИКТЕ ИЛИ ИНОЙ СИТУАЦИИ, ВОЗНИКШИМ ИЗ-ЗА ИСПОЛЬЗОВАНИЯ ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ ИЛИ ИНЫХ ДЕЙСТВИЙ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ.
                ''')
        self.nav_drawer._toggle()
        previous_screen = self.manager.current
        self.manager.current = 'show license'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(
                previous_screen)]]
        self.screen.ids.action_bar.title = \
            self.translation._('MIT LICENSE')

    def select_locale(self):
        '''Выводит окно со спискои имеющихся языковых локализаций для
        установки языка приложения.'''

        def select_locale(*args):
            '''Устанавливает выбранную локализацию.'''

            # args: ('Language\n', 'item').
            select_language = args[0].replace('\n', '')
            for items in self.dict_language.items():
                if select_language in items:
                    self.lang = items[0]
                    self.config.set('General', 'language', self.lang)
                    self.config.write()

        dict_info_locales = {}
        for locale in self.dict_language.keys():
            dict_info_locales[self.dict_language[locale]] = \
                ['', 'data/locales/flags/%s.png' % locale]

        card(
            Lists(
                dict_items=dict_info_locales,
                events_callback=select_locale, flag='three_list_custom_icon'
            )
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

    def on_lang(self, instance, lang):
        self.translation.switch_lang(lang)

    def on_pause(self):
        '''Ставит приложение на 'паузу' при выходе из него.
        В противном случае запускает программу заново.'''

        return True

pattern_whom_comment = re.compile(r'\[id\d+\|\w+\]', re.UNICODE)
pattern_replace_link = re.compile(r'(?#Protocol)(?:(?:ht|f)tp(' \
                             '?:s?)\:\/\/|~\/|\/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:\/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|\/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,'
                                  '*:=]|%[a-f\d]{2})*)?')
