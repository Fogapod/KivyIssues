# -*- coding: utf-8 -*-
#
# Создает и компанует выджеты для вывода постов группы
# или комментариев к ним.
#

import time
import re

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.utils import get_hex_from_color
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty,\
    BooleanProperty, NumericProperty, ListProperty

from libs.uix.canvasadd import canvas_add as add_canvas
from libs.uix.lists import RightButton
from libs.createpaginator import create_paginator
from libs.uix.kv.activity.baseclass.iconcomments import IconCountComments

from kivymd.card import MDSeparator


class BoxPosts(FloatLayout):

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
    '''Количество получаемых постов/комментариев.'''

    current_number_page = NumericProperty()
    '''Выбранная страница.'''

    commented_post_info = ListProperty()
    '''Имя, аватар, дата, текст комментируемого поста.'''

    post_id = StringProperty()
    '''id поста для которого выводится список комментариев.'''

    list_labels_posts = []
    '''Список лейблов постов.'''

    def __init__(self, **kwargs):
        super(BoxPosts, self).__init__(**kwargs)

        self.paginator_pages = None
        # Label с количеством комментариев к посту.
        self.label_count_comments = None

        if self.comments:
            self.ids.list_posts.spacing = 0

    def create_posts(self, items_posts):
        # Добавляем в шапку списка комментариев комментируемый пост.
        if self.comments:
            self.add_info_for_post(add_commented_post=True)

        for items_dict in items_posts:
            post, author_name = self.add_info_for_post(items_dict)

            if self.only_questions:  # пост пользователя
                if self._app.data.user_name == author_name:
                    self.ids.list_posts.add_widget(post)
            else:  # все посты
                self.ids.list_posts.add_widget(post)

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

                post.height = \
                    dp(value[1] + post.ids.title_post.height +
                       self.label_count_comments.height)

            def set_height_post(instance, value):
                '''Смотрите метод open_real_size_post класса Post.'''

                if post.not_set_height_label:
                    return

                if instance not in self.list_labels_posts and \
                        value != [0, 0]:
                    self.list_labels_posts.append(instance)
                    post._texture_height = value[1]
                else:
                    # Устанавливает фиксированную высоту текста поста.
                    instance.text_size = \
                        (dp(self._app.window.width - 30), dp(70))

            if not add_commented_post:  # для постов/комментариев
                # Имя, аватар, дата, текст.
                author_name = \
                    self.profiles_dict[items_dict['from_id']]['author_name']
                post.ids.title_post.icon = \
                    self.profiles_dict[items_dict['from_id']]['avatar']
                post.ids.title_post.text = author_name
                date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                    items_dict['date']
                    )
                )
                post.ids.title_post.secondary_text = date
                # FIXME: UnicodeError: A Unicode character above '\uFFFF'
                # was found; not supported - ошибка при присутствии в тексте
                # постов/комментариев ебаных смайлов (как их я их ненавижу)
                # при использовании третьей версии Python.
                post.ids.text_posts.text = text_post
                # print(text_post.encode().decode("utf-8", 'ignore'))
                post.ids.text_posts.bind(
                    texture_size=set_height_post
                )
            else:  # для шапки комментируемого поста
                author_name = self.commented_post_info[0]
                post.ids.title_post.text = author_name
                post.ids.title_post.icon = self.commented_post_info[1]
                post.ids.title_post.secondary_text = \
                    self.commented_post_info[2]
                post.ids.text_posts.text = text_post + u'\n'
                # Выделяем имя автора комментрируемого поста канвасом
                # темнее, чем комментарии к нему.
                canvas_color = [
                    0.9686274509803922, 0.9686274509803922,
                    0.9686274509803922, 1
                ]
                add_canvas(post.ids.title_post, canvas_color)
                post.ids.text_posts.bind(
                    texture_size=set_height_commented_post
                )

                # Строка с количеством комментариев к посту.
                box_comments = AnchorLayout(size_hint_y=None, height=dp(20))
                self.label_count_comments = Label(
                    text=self._app.data.string_lang_count_comments.format(
                        self.count_issues), font_size='11sp'
                )
                add_canvas(box_comments, self._app.theme_cls.primary_color)

                box_comments.add_widget(self.label_count_comments)
                post.add_widget(box_comments)
                self.ids.list_posts.add_widget(post)

                return author_name

        def add_icon_status():
            '''Добавляем иконку статуса пользователя:
            с компьютера/мобильного/offline.'''

            if not add_commented_post:
                if self.profiles_dict[
                        items_dict['from_id']]['author_online']:
                    icon = self._app.data.device_online[
                        self.profiles_dict[items_dict['from_id']]['device']
                    ]
                else:
                    icon = self._app.data.device_online[0]
            else:
                icon = self._app.data.device_online[0]

            post.ids.title_post.add_widget(RightButton(source=icon))

        if items_dict is None:
            items_dict = {}

        post = self._app.Post(height=dp(200), _box_posts=self)

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
                text_post = u'[ref=Text post][b][color=%s]\n%s[/b][/color]' \
                            '%s[/ref]' %(
                    get_hex_from_color(self._app.theme_cls.primary_color),
                    whom_name, self._app.mark_links_in_post(text_post))
            else:
                text_post = u'\n' + text_post

            if 'reply_to_comment' in items_dict:
                commented_post_id = items_dict['id']
            else:
                commented_post_id = ''

            # Подпись 'Ответить'.
            answer_label = Label(
                text='[ref={answer}]{answer}[/ref]'.format(
                    answer=self._app.data.string_lang_answer_on_post),
                markup=True, halign="left", font_size='11sp',
                color=self._app.theme_cls.primary_color,
                )
            whom_name = \
                self.profiles_dict[items_dict['from_id']]['author_name']
            answer_label.bind(
                size=answer_label.setter('text_size'),
                on_ref_press=lambda *args: post.answer_on_comments(
                    self.post_id, self.count_issues, commented_post_id,
                    whom_name, self.ids.input_text_form
                )
            )
            post.add_widget(answer_label)
        # Для комментируемого поста.
        elif self.comments and add_commented_post:
            text_post = self._app.mark_links_in_post(
                u'\n' + self.commented_post_info[3]
            )
        # Для поста.
        else:
            text_post = u'[ref=Post]%s[/ref]' %(
                self._app.mark_links_in_post(items_dict['text'])
            )
            # Иконка количества коментариев к посту.
            post.add_widget(
                IconCountComments(
                    callback=lambda *args: post.show_comments(
                        str(items_dict['id']),
                        str(items_dict['comments']['count'])
                    )
                )
            )
            # Количество коментариев к посту.
            post.children[0].ids.comments_post.text = \
                str(items_dict['comments']['count'])
            # Тень поста/комментария.
            add_canvas(post, [0, 0, 0, .2], shift=(2.5, 3))

        # Фон поста/комментария.
        add_canvas(post, self._app.data.list_color)
        author_name = add_name_avatar_date_post()
        add_icon_status()

        # Добавляем разделительную линию между комментариями.
        if self.comments:
            post.add_widget(MDSeparator())

        return post, author_name

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
        self.ids.box_posts.add_widget(paginator_box)
        add_canvas(paginator_box, self._app.data.list_color)

        return paginator_pages