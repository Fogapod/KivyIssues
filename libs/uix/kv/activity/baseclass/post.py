# -*- coding: utf: 8 -*-

from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty

from libs.programclass.showposts import ShowPosts
from libs.uix.dialogs import card
from libs.uix.kv.activity.baseclass.form_input_text import FormInputText
from libs.vkrequests import create_comment


class Post(BoxLayout):
    _app = ObjectProperty()
    '''<class 'program.Program'>'''

    _texture_height = NumericProperty()
    '''Реальные размеры (texture_size) лейбла текста поста:
    Используются для развертывание текста поста при клике на него.'''

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)
        self.commented_post_id = ''
        self.not_set_height_label = False
        self.ids.title_post.ids._lbl_primary.bold = True
        self.ids.title_post.ids._lbl_secondary.font_size = '11sp'

    def tap_on_text_or_link_post(self, *args):
        '''Вызывается при тапе на текст поста/комментария/ссыки.'''

        instance, text_link = args[0]

        if text_link == 'Post':
            self.open_real_size_post()

    def answer_on_comments(self, *args):
        def callback(flag):
            print('Call with flag', flag)
            # Удаляем имя адресата и кнопку удаления адресата.
            if flag == 'DELL':
                print('DELL')
                form.ids.box.remove_widget(form.ids.label_to)
                form.ids.box.remove_widget(form.ids.delete_whom)
                self.commented_post_id = ''
            elif flag == 'SEND':
                print(self.commented_post_id)
                text_answer = form.ids.text_input.text
                if text_answer.isspace() or text_answer == '':
                    dialog.dismiss()
                    return
                result = create_comment(
                    {'file': None, 'image': None, 'text': text_answer},
                    post_id=post_id, reply_to=self.commented_post_id
                )
                print(result)

        # type post_id: str;
        # param post_id: id комментируемого поста;
        # ----------------------------------------
        # type commented_post_id: str;
        # param commented_post_id: id комментария для которого пишется ответ;
        # ----------------------------------------
        # type whom_name: list;
        # param whom_name: кому - ['First name', 'Last name'];
        post_id, self.commented_post_id, whom_name = args

        print('Call answer_on_comments:',
              post_id, self.commented_post_id, whom_name)
        form = FormInputText()
        form.ids.text_input.background_normal = 'data/images/text_input.png'
        form.avatar_icon = 'data/images/avatar.png'
        form.add_file_icon = 'data/images/paperclip.png'
        form.add_foto_icon = 'data/images/camera.png'
        form.delete_whom_icon = 'data/images/exit.png'
        form.label_color = self._app.theme_cls.primary_color
        form.button_text_send = 'Отправить'
        form.label_text_to = whom_name.split(' ')[0]
        form.callback = callback
        dialog = card(form, size=(.99, .3))

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

        # :type post_id: str;
        # :param post_id: id поста для которого выводится список комментариев;

        # :type count_comment: str;
        # :param count_comment: количество комментириев;
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
