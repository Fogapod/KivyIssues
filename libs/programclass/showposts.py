# -*- coding: utf-8 -*-
#
# Получает данные о постах и комментариях группы с сервера
# и управляет созданием экранов с полученными данными.
#

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from libs.programdata import thread


class ShowPosts(object):

    def __init__(self, app=None, count_issues_comments='1',
                 only_questions=False, commented_post_info=None,
                 comments=False, post_id='', current_number_page=1):
        '''
        :param app: <class 'program.Program'>;
        :param count_issues_comments: количество получаемых постов/комм-ев;
        :param only_questions: все или только свои посты;
        :param comments: если True - выводим комментарии;
        :param post_id: id поста для которого выводится список комментариев;
        :param current_number_page: выбранная страница;
        :param commented_post_info: [имя, аватар, дата, текст
                                     комментируемого поста[;
        '''

        self._app = app
        self.count_issues_comments = count_issues_comments
        self.only_questions = only_questions
        self.comments = comments
        self.post_id = post_id
        self.current_number_page = current_number_page
        self.profiles_dict = {}
        self.items_list = None
        self.index_start = 0
        self.index_end = current_number_page * self._app.data.count_issues
        # Имя предыдущего экрана.
        self.previous_screen = self._app.manager.current

        if commented_post_info is None:
            self.commented_post_info = []
        else:
            self.commented_post_info = commented_post_info

    def set_chevron_back_screen(self):
        '''Устанавливает шеврон возврата к предыдущему экрану в ToolBar.'''

        if self._app.screen.ids.action_bar.right_action_items[0][0] != \
                'comment-outline':
            self._app.screen.ids.action_bar.right_action_items = \
                [['comment-outline', lambda x: None]]
        self._app.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self._app.back_screen(
                self.previous_screen)]]

    @thread
    def _set_info_for_post(self):
        '''Получает и присваивает json с информацией о постах/комментариях
        атрибуту items_list.'''

        self.profiles_dict, self.items_list = \
            self._app.get_info_from_post(
                self.count_issues_comments, self.post_id, self.comments
            )

    def create_posts(self, name_screen):
        '''Создает и выводит новый экран с постами/комментариями группы.'''

        def check_posts_dict(interval):
            if self.items_list:
                box_posts = self._app.BoxPosts(
                    profiles_dict=self.profiles_dict,
                    count_issues=self.count_issues_comments,
                    only_questions=self.only_questions,
                    current_number_page=self.current_number_page,
                    commented_post_info=self.commented_post_info,
                    comments=self.comments,
                    post_id=self.post_id
                )
                box_posts.create_posts(
                    self.items_list[self.index_start:self.index_end]
                )
                box_posts.paginator_pages.bind(
                    on_ref_press=lambda *args: self.jump_to_page(args)
                )

                #self.previous_screen = self._app.manager.current
                #self.set_chevron_back_screen()

                screen = Screen(name=name_screen)
                screen.add_widget(box_posts)
                self._app.manager.add_widget(screen)
                self._app.manager.current = name_screen

                Clock.unschedule(check_posts_dict)
                self._app.dialog_progress.dismiss()

        self._app.show_progress(text=self._app.data.string_lang_wait)

        if not self._app.manager.has_screen(name_screen):
            self._set_info_for_post()

        Clock.schedule_interval(check_posts_dict, 0)

    def jump_to_page(self, *args):
        '''Вызывает функцию вывода постов, устанавливая индексы среза
        для списка постов согласно выбранной странице пагинатора
        и количеству постов, которое нужно выводить на экрнан.'''

        select_number_page = int(args[0][1])
        if self.current_number_page == select_number_page:
            return

        self.index_end = select_number_page * self._app.data.count_issues
        self.index_start = self.index_end - self._app.data.count_issues
        self.current_number_page = select_number_page
        self.show_posts()

    def show_posts(self):
        if not self.comments:
            name_screen = \
                'box posts page ' + str(self.current_number_page)
        else:
            name_screen = \
                'box comments page ' + str(self.current_number_page)

        if self._app.manager.has_screen(name_screen):
            self._app.manager.current = name_screen
        else:
            self.create_posts(name_screen)
