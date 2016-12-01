# -*- coding: utf-8 -*-

import time

from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import get_hex_from_color
from kivy.metrics import dp

from libs.paginator import paginator
from libs.uix.canvasadd import canvas_add
from libs.programdata import thread
from libs.uix.lists import RightMDIcon


class BoxPosts(Screen):

    profiles_dict = None
    items_dict = None
    current_number_page = 1
    old_screen = StringProperty()

    def _back_screen(self):
        self.clear_box_posts()
        self.app.back_screen(self.old_screen)

    def clear_box_posts(self):
        self.ids.box_posts.clear_widgets()
        paginator = self.ids.box_paginator.children[0]
        self.ids.box_paginator.remove_widget(paginator)
        self.current_number_page = 1

    def on_enter(self):
        if self.app.screen.ids.action_bar.right_action_items[0][0] != \
                'comment-outline':
            self.app.screen.ids.action_bar.right_action_items = \
                [['comment-outline', lambda x: None]]
        self.app.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self._back_screen()]]

    @thread
    def _get_info_from_post(self, count_issues):
        self.profiles_dict, self.items_dict = \
            self.app.get_info_from_post(count_issues=count_issues)

    def show_posts(self, count_issues, only_questions=False):
        '''
        :type count_issues: str;
        :param count_issues: количество получаемых постов;
        :param only_questions: все или только свои посты;

        '''

        def check_posts_dict(interval):
            if self.profiles_dict:
                self.create_posts(
                    count_issues,
                    self.items_dict[0:self.app.data.count_issues],
                    only_questions
                )
                self.old_screen = self.app.manager.current
                self.app.manager.current = 'box posts'
                Clock.unschedule(check_posts_dict)
                self.app.dialog_progress.dismiss()

        self.app = self.manager._app
        self.app.show_progress(text=self.app.data.string_lang_wait)
        self._get_info_from_post(count_issues)
        Clock.schedule_interval(check_posts_dict, 0)

    def create_posts(self, count_issues, items_posts, only_questions):
        '''Создает и компанует выджеты для вывода постов группы.'''

        for items_dict in items_posts:
            box_posts = self.app.Post(size_hint_y=None)
            box_posts.ids.title_post.ids._lbl_primary.bold = True
            box_posts.ids.title_post.ids._lbl_secondary.font_size = '11sp'

            author_name = \
                self.profiles_dict[items_dict['from_id']]['author_name']
            box_posts.ids.title_post.icon = \
                self.profiles_dict[items_dict['from_id']]['avatar']
            box_posts.ids.title_post.text = author_name
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                items_dict['date']
                )
            )
            box_posts.ids.title_post.secondary_text = date

            if self.profiles_dict[items_dict['from_id']]['author_online']:
                icon = self.app.data.device_online[
                    self.profiles_dict[items_dict['from_id']]['device']
                ]
            else:
                icon = self.app.data.device_online[0]
            box_posts.ids.title_post.add_widget(
                RightMDIcon(
                    icon=icon, theme_text_color='Custom',
                    text_color=self.app.theme_cls.primary_color
                )
            )

            box_posts.ids.text_posts.text = \
                '[ref=Text post]{}[/ref]'.format(
                    self.app.mark_links_in_post(items_dict['text'])
                )
            box_posts.ids.comments_post.text = \
                str(items_dict['comments']['count'])

            if only_questions:
                if self.app.data.user_name == author_name:
                    self.ids.box_posts.add_widget(box_posts)
            else:
                self.ids.box_posts.add_widget(box_posts)

        if only_questions:
            count_issues = self.ids.box_posts.children.__len__()

        paginator_box = BoxLayout(size_hint_y=None, height=dp(30))
        paginator_string = self.create_paginator(
            number_posts=int(count_issues), pages=self.app.data.count_issues,
            current_number_page=self.current_number_page
        )
        paginator_pages = Label(text=paginator_string, markup=True)
        paginator_pages.bind(
            on_ref_press=lambda *args: self.jump_to_page(
                args, count_issues, only_questions
            )
        )
        paginator_box.add_widget(paginator_pages)
        self.ids.box_paginator.add_widget(paginator_box)
        canvas_add(paginator_box, self.app.data.list_color)

    def create_paginator(self, number_posts=1, current_number_page=1,
                         pages=20):
        '''Формирует нумерацию страниц и помечает выбраную.

        :param current_number_page: номер текущей страницы;
        :param number_posts: количество записей;
        :param pages: количество записей на одной странице;

        '''

        number_pages = int(round(number_posts / pages))
        if not number_pages:
            number_pages = 1
        print(number_pages, current_number_page)
        list_pages = paginator(number_pages, current_number_page)

        build_pages = ""
        for number_page in list_pages:
            try:
                number_page = \
                    int(number_page.replace("[", "").replace("]", ""))

                if current_number_page == number_page:
                    color = \
                        get_hex_from_color(self.app.theme_cls.primary_color)
                else:
                    color = self.app.data.text_color
            except ValueError:
                color = get_hex_from_color(self.app.theme_cls.primary_color)

            build_pages += \
                '[color={}][ref={number_page}]{number_page}[/ref] '.format(
                    color, number_page=number_page)

        return build_pages

    def jump_to_page(self, *args):
        '''Очищает экран с вопросами группы, вызывает функцию вывода постов,
        передавая в качестве аргумента срез списка постов согласно выбранной
        странице пагинатора и количеству постов, которое нужно выводить на
        экрнан.

        '''

        # TODO: сделать вызов функции в потоке, так как бар прогресса
        # зависает при постороении интерфейса.
        def _jump_to_page(interval):
            self.current_number_page = value
            self.clear_box_posts()
            self.create_posts(
                count_issues, self.items_dict[index_of - 20:index_of],
                only_questions
            )
            self.app.dialog_progress.dismiss()

        value = int(args[0][1])

        if self.current_number_page == value:
            return

        count_issues = args[1]
        only_questions = args[2]
        index_of = value * 20

        Clock.schedule_once(
            lambda x: self.app.show_progress(
                text=self.app.data.string_lang_wait), 0
        )
        Clock.schedule_once(_jump_to_page, 0.1)
