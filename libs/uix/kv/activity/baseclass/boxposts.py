# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import get_hex_from_color
from kivy.metrics import dp

from libs.paginator import paginator
from libs.uix.canvasadd import canvas_add


class BoxPosts(Screen):

    def on_enter(self):
        self.app.screen.ids.action_bar.right_action_items = \
            [['comment-outline', lambda x: None]]

    def show_posts(self, count_issues):
        '''
        :type count_issues: str;
        :param count_issues: количество получаемых постов;

        '''

        self.create_posts(count_issues)
        self.app.manager.current = 'box posts'

    def create_posts(self, count_issues):
        '''Создает и компанует выджеты для вывода постов группы.'''

        self.app = self.manager._app
        posts_dict = self.app.get_info_from_post(count_issues)

        for author in posts_dict.keys():
            box_posts = self.app.Post(size_hint_y=None)
            box_posts.ids.title_post.ids._lbl_primary.bold = True
            box_posts.ids.title_post.ids._lbl_secondary.font_size = '11sp'

            box_posts.ids.title_post.icon = posts_dict[author]['avatar']
            box_posts.ids.title_post.text = author
            box_posts.ids.title_post.secondary_text = \
                posts_dict[author]['date']
            box_posts.ids.text_posts.text = posts_dict[author]['text']
            box_posts.ids.comments_post.text = \
                str(posts_dict[author]['comments'])
            self.ids.box_posts.add_widget(box_posts)

        paginator_box = BoxLayout(
            size_hint=(None, None),
            size=(dp(self.app.window.size[0] - 10), dp(30))
        )
        paginator_pages = Label(
            text=self.create_paginator(number_posts=int(count_issues)),
            markup=True, on_ref_press=self.jump_to_page
        )
        paginator_box.add_widget(paginator_pages)
        self.ids.box_paginator.add_widget(paginator_box)
        canvas_add(paginator_box, self.app.data.list_color, (5, 0))

    def create_paginator(self, number_posts=1, current_number_page=1):
        '''Формирует нумерацию страниц и помечает выбраную.

        :param current_number_page: номер текущей страницы;
        :param number_posts: количество страниц;

        '''

        list_pages = paginator(number_posts, current_number_page)

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
