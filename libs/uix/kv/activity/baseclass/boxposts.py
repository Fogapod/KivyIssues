# -*- coding: utf-8 -*-
#
# Создает и компанует выджеты для вывода постов группы
# или комментариев к ним.
#

import time
import re

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.utils import get_hex_from_color
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty,\
    BooleanProperty, NumericProperty, ListProperty

from libs.uix.canvasadd import canvas_add as add_canvas
from libs.uix.lists import RightButton
from libs.uix.kv.activity.baseclass.iconcomments import IconCountComments
from libs.createpaginator import create_paginator

from kivymd.card import MDSeparator


class BoxPosts(BoxLayout):

    _app = ObjectProperty()
    '''<class 'program.Program'>'''

    profiles_dict = ObjectProperty()
    '''Данные о постах/комментариях, полученные с сервера функциями
    get_issues и get_comments из модуля vkrequests.'''

    only_questions = BooleanProperty()
    '''Все или только свои посты.'''

    comments = BooleanProperty()
    '''Если True - выводим комментарии.'''

    count_issues = StringProperty()
    '''Лоличество получаемых постов/комментариев.'''

    current_number_page = NumericProperty()
    '''Ввыбранная страница.'''

    commented_post_info = ListProperty()
    '''Имя, аватар, дата, текст комментируемого поста.'''

    post_id = StringProperty()
    '''id поста для которого выводится список комментариев.'''

    list_labels_posts = []
    '''Список лейблов постов.'''

    def __init__(self, **kwargs):
        super(BoxPosts, self).__init__(**kwargs)

        self.paginator_pages = None
        if self.comments:
            self.ids.list_posts.spacing = 0

    def create_posts(self, items_posts):
        # Добавляем в шапку списка комментариев комментируемый пост.
        if self.comments:
            self.add_info_for_post(add_commented_post=True)

        for items_dict in items_posts:
            box_posts, author_name = self.add_info_for_post(items_dict)

            if self.only_questions:  # пост пользователя
                if self._app.data.user_name == author_name:
                    self.ids.list_posts.add_widget(box_posts)
            else:  # все посты
                self.ids.list_posts.add_widget(box_posts)

        if self.only_questions:
            self.count_issues = self.ids.list_posts.children.__len__()

        self.paginator_pages = self.add_paginator()

    def add_info_for_post(self, items_dict=None, add_commented_post=False):
        '''Добавляет аватар, имя автора, дату поста
        и иконку статуса автора (online/offline).'''

        def add_name_avatar_date_post():
            '''Добавляет имя, аватар, дату автора поста/комментария,'''

            def set_height_commented_post(instance, value):
                '''Смотрите метод set_height_post.'''

                box_posts.height = \
                    dp(value[1] + box_posts.ids.title_post.height + \
                    count_comments.height)

            def set_height_post(instance, value):
                '''Смотрите метод open_real_size_post класса Post.'''

                if box_posts.not_set_height_label:
                    return

                if instance not in self.list_labels_posts and \
                        value != [0, 0]:
                    self.list_labels_posts.append(instance)
                    box_posts._texture_height = value[1]
                else:
                    # Устанавливает фиксированную высоту текста поста.
                    instance.text_size = \
                        (dp(self._app.window.width - 30), dp(70))

            if not add_commented_post:  # для постов/комментариев
                # Имя, аватар, дата, текст.
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
                box_posts.ids.text_posts.text = text_post
                box_posts.ids.text_posts.bind(
                    texture_size=set_height_post
                )
            else:  # для шапки комментируемого поста
                author_name = self.commented_post_info[0]
                box_posts.ids.title_post.text = author_name
                box_posts.ids.title_post.icon = self.commented_post_info[1]
                box_posts.ids.title_post.secondary_text = \
                    self.commented_post_info[2]
                box_posts.ids.text_posts.text = text_post + '\n'
                # Выделяем имя автора комментрируемого поста канвасом
                # темнее, чем комментарии к нему.
                canvas_color = [
                    0.9686274509803922, 0.9686274509803922,
                    0.9686274509803922, 1
                ]
                add_canvas(box_posts.ids.title_post, canvas_color)
                box_posts.ids.text_posts.bind(
                    texture_size=set_height_commented_post
                )

                # Строка с количеством комментариев к посту.
                box_comments = AnchorLayout(size_hint_y=None, height=dp(20))
                count_comments = Label(
                    text=self._app.data.string_lang_count_comments.format(
                        self.count_issues), font_size='11sp'
                )
                add_canvas(box_comments, self._app.theme_cls.primary_color)

                box_comments.add_widget(count_comments)
                box_posts.add_widget(box_comments)
                self.ids.list_posts.add_widget(box_posts)

                return author_name

        def add_icon_status():
            '''Добавляем иконку статуса пользователя:
            с компьютера/мобильного/offline.'''

            if not add_commented_post:
                if self.profiles_dict[items_dict['from_id']]['author_online']:
                    icon = self._app.data.device_online[
                        self.profiles_dict[items_dict['from_id']]['device']
                    ]
                else:
                    icon = self._app.data.device_online[0]
            else:
                icon = self._app.data.device_online[0]

            box_posts.ids.title_post.add_widget(RightButton(source=icon))

        if items_dict is None:
            items_dict = {}

        box_posts = self._app.Post(height=dp(200))

        # Для комментариев.
        if self.comments and not add_commented_post:
            text_post = items_dict['text']
            # Ищем в комментариях, кому адресованно -
            # подстроку вида '[id12345|NameAuthor]'.
            count = re.match(self._app.data.pattern_whom_comment, text_post)
            if count:
                count = count.group()
                # id и имя автора, которому написан комментарий.
                whom_id, whom_name = \
                    count.replace('[', '').replace(']', '').split('|')
                text_post = text_post.replace(count, '')
                text_post = '[ref=Text post][b][color={}]\n{}[/b][/color]' \
                            '{}[/ref]'.format(
                    get_hex_from_color(self._app.theme_cls.primary_color),
                    whom_name, self._app.mark_links_in_post(text_post))
            else:
                if self._app.data.PY2:
                    text_post = u'\n{}'.format(text_post)
                else:
                    text_post = '\n{}'.format(text_post)

            if 'reply_to_comment' in items_dict:
                commented_post_id = items_dict['id']
            else:
                commented_post_id = ''

            answer_label = Label(
                text='[ref={answer}]{answer}[/ref]'.format(
                    answer=self._app.data.string_lang_answer_on_post),
                markup=True, halign="left", font_size='11sp',
                color=self._app.theme_cls.primary_color,
                )
            answer_label.bind(
                size=answer_label.setter('text_size'),
                on_ref_press=lambda post_id, commented_id_post:
                    box_posts.answer_on_comments(
                        self.post_id, commented_post_id
                    )
            )
            box_posts.add_widget(answer_label)
        # Для комментируемого поста.
        elif self.comments and add_commented_post:
            if self._app.data.PY2:
                text_post = self._app.mark_links_in_post(
                    u'\n{}'.format(self.commented_post_info[3])
                )
            else:
                text_post = self._app.mark_links_in_post(
                    '\n{}'.format(self.commented_post_info[3])
                )
        # Для поста.
        else:
            if self._app.data.PY2:
                text_post = u'[ref=Post]{}[/ref]'.format(
                    self._app.mark_links_in_post(items_dict['text'])
                )
            else:
                text_post = '[ref=Post]{}[/ref]'.format(
                    self._app.mark_links_in_post(items_dict['text'])
                )
            # Иконка количества коментариев к посту.
            box_posts.add_widget(
                IconCountComments(
                    callback=lambda *args: box_posts.show_comments(
                        str(items_dict['id']),
                        str(items_dict['comments']['count'])
                    )
                )
            )
            # Количество коментариев к посту.
            box_posts.children[0].ids.comments_post.text = \
                str(items_dict['comments']['count'])
            # Тень поста/комментария.
            add_canvas(box_posts, [0, 0, 0, .2], shift=(2.5, 3))

        # Фон поста/комментария.
        add_canvas(box_posts, self._app.data.list_color)
        author_name = add_name_avatar_date_post()
        add_icon_status()

        # Добавляем разделительную линию между комментариями.
        if self.comments:
            box_posts.add_widget(MDSeparator())

        return box_posts, author_name

    def add_paginator(self):
        '''Добавляет бокс с номерами страниц.'''

        paginator_box = BoxLayout(size_hint_y=None, height=dp(30))
        paginator_string = create_paginator(
            number_posts=int(self.count_issues),
            pages=self._app.data.count_issues,
            current_number_page=self.current_number_page,
            link_color=get_hex_from_color(self._app.theme_cls.primary_color),
            number_color=self._app.data.text_color
        )
        paginator_pages = Label(text=paginator_string, markup=True)
        paginator_box.add_widget(paginator_pages)
        self.add_widget(paginator_box)
        add_canvas(paginator_box, self._app.data.list_color)

        return paginator_pages