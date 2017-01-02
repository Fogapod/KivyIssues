# -*- coding: utf: 8 -*-

import time

from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty

from libs.programclass.showposts import ShowPosts


class Post(BoxLayout):
    _app = ObjectProperty()
    '''<class 'program.Program'>'''

    _texture_height = NumericProperty()
    '''Реальные размеры (texture_size) лейбла текста поста:
    Используются для развертывание текста поста при клике на него.'''

    _box_posts = ObjectProperty()
    '''<class 'libs.uix.kv.activity.baseclass.boxposts.BoxPosts'>'''

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)
        self.not_set_height_label = False
        self.ids.title_post.ids._lbl_primary.bold = True
        self.ids.title_post.ids._lbl_secondary.font_size = '11sp'

    def tap_on_text_or_link_post(self, *args):
        '''Вызывается при тапе на текст поста/комментария/ссыки.'''

        instance, text_link = args[0]
        if text_link == 'Post':
            self.open_real_size_post()
        # TODO: добавить обработку ссылок в тексте.

    def update_post(self, text_answer, post_id, whom_name):
        '''Добавляет в бокс списка комментариев только что отправленное
        сообщение.'''

        items_dict = {'text': text_answer, 'id': post_id,
                      'date': time.time(), 'from_id': 1}
        self._box_posts.profiles_dict = \
            {1:
                {'author_name': whom_name, 'author_online': 1,
                 'avatar': self.ids.title_post.icon, 'device': 'mobile'}}

        self._box_posts.comments = True
        # Увеличиваем счетчик комментариев.
        self._box_posts.label_count_comments.text = \
            self._app.data.string_lang_count_comments.format(
                str(int(self._box_posts.count_issues) + 1)
            )
        post, author_name = self._box_posts.add_info_for_post(
            items_dict=items_dict, add_commented_post=False,
        )
        self._box_posts.ids.list_posts.add_widget(post)

    def answer_on_comments(self, *args):
        # type post_id: str;
        # param post_id: id комментируемого поста;
        # ----------------------------------------
        # type commented_post_id: str;
        # param commented_post_id: id комментария для которого пишется ответ;
        # ----------------------------------------
        # type whom_name: list;
        # param whom_name: кому - 'First name Last name';
        post_id, count_comment, \
            commented_post_id, whom_name, input_text_form = args

        self._app.show_input_form(input_text_form)
        input_text_form.ids.text_input.message = \
            self._app.data.string_lang_for + whom_name
        input_text_form.ids.text_input.focus = True
        input_text_form.ids.text_input.text = '%s, ' % whom_name.split(' ')[0]
        input_text_form.callback = \
            lambda *args: self._app.callback_for_input_text(
                args, post_id, commented_post_id, input_text_form, self,
                whom_name
            )

    def open_real_size_post(self):
        '''Устанавливает высоту поста в соответствии с высотой текстуры
        лейбла поста. Изменяет размеры области для текста поста.'''

        def none(*args):
            '''Вызывается при повторном клике на текст поста.'''

        self.not_set_height_label = True
        height = self._texture_height // 1.6

        if height < self.height:
            return

        # Изменяем размер тела поста.
        self.height = height
        # Изменяем область для текста.
        # TODO: при большом размере тексте остается большая пустая область -
        # соотнести высоту тела поста и высоту текстуры текста.
        self.ids.text_posts.text_size = \
            (dp(self._app.window.width - 30),
             dp((self.height - self.ids.title_post.height) - 30))
        self.ids.text_posts.text = u'\n' + self.ids.text_posts.text
        self.ids.text_posts.bind(
            on_ref_press=lambda instance, text_link: none
        )

    def show_comments(self, *args):
        """Вызывается при клике на иконку комментариев под текстом поста.
        Выводит на экран список комментариев к посту."""

        # type post_id: str;
        # param post_id: id поста для которого выводится список комментариев;
        # ----------------------------------------
        # type count_comment: str;
        # param count_comment: количество комментириев;
        post_id, count_comment = args

        name_author = self.ids.title_post.text
        avatar_author = self.ids.title_post.icon
        date_post = self.ids.title_post.secondary_text
        text_post = self.ids.text_posts.text
        commented_post_info = \
            [name_author, avatar_author, date_post, text_post]

        ShowPosts(app=self._app, post_id=post_id, comments=True,
                  count_issues_comments=count_comment,
                  commented_post_info=commented_post_info).show_posts()
