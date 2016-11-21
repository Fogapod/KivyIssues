# -*- coding: utf-8 -*-

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import get_hex_from_color
from kivy.metrics import dp

from libs.paginator import paginator
from libs.uix.canvasadd import canvas_add
from libs.programdata import thread


class BoxPosts(Screen):

    posts_dict = None

    def set_screen_previous(self):
        self.manager.current = self.old_screen

    def on_enter(self):
        self.app.screen.ids.action_bar.right_action_items = \
            [['comment-outline', lambda x: None]]
        self.app.screen.ids.action_bar.left_action_items = \
            [['chevron-left', self.set_screen_previous]]

    @thread
    def _get_info_from_post(self, count_issues):
        self.posts_dict = self.app.get_info_from_post(count_issues)

    def show_posts(self, count_issues):
        '''
        :type count_issues: str;
        :param count_issues: количество получаемых постов;

        '''

        def check_posts_dict(interval):
            if self.posts_dict:
                self.app.dialog_progress.dismiss()
                self.create_posts(count_issues)
                self.old_screen = self.app.manager.current
                self.app.manager.current = 'box posts'
                self.posts_dict = None
                Clock.unschedule(check_posts_dict)

        self.app = self.manager._app
        self.app.show_progress(text=self.app.data.string_lang_wait)
        self._get_info_from_post(count_issues)
        Clock.schedule_interval(check_posts_dict, 0)

    def create_posts(self, count_issues):
        '''Создает и компанует выджеты для вывода постов группы.'''

        for author in self.posts_dict.keys():
            box_posts = self.app.Post(size_hint_y=None)
            box_posts.ids.title_post.ids._lbl_primary.bold = True
            box_posts.ids.title_post.ids._lbl_secondary.font_size = '11sp'

            box_posts.ids.title_post.icon = self.posts_dict[author]['avatar']
            box_posts.ids.title_post.text = author
            box_posts.ids.title_post.secondary_text = \
                self.posts_dict[author]['date']
            box_posts.ids.text_posts.text = self.posts_dict[author]['text']
            box_posts.ids.comments_post.text = \
                str(self.posts_dict[author]['comments'])
            self.ids.box_posts.add_widget(box_posts)

        paginator_width = dp(self.app.window.size[0] - 10)
        paginator_box = BoxLayout(
            size_hint=(None, None), size=(paginator_width, dp(30))
        )
        paginator_pages = Label(
            text=self.create_paginator(number_posts=int(count_issues)),
            markup=True, on_ref_press=self.jump_to_page, halign='center',
            text_size=(paginator_width, None), size_hint=(None, None)
        )
        paginator_pages.bind(texture_size=paginator_pages.setter('size'))
        paginator_box.add_widget(paginator_pages)
        self.ids.box_paginator.add_widget(paginator_box)
        canvas_add(paginator_box, self.app.data.list_color, (5, 0))

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

    def jump_to_page(self, instance, value):
        print(instance, value)
