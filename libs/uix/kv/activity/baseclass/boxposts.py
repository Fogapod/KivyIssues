from kivy.uix.screenmanager import Screen


class BoxPosts(Screen):

    def show_posts(self, count_issues):
        '''
        :type count_issues: str;
        :param count_issues: количество получаемых постов;

        '''

        app = self.manager._app
        posts_dict = app.get_info_from_post(count_issues)

        for author in posts_dict.keys():
            box_posts = app.Post(size_hint_y=None)
            box_posts.ids.title_post.icon = posts_dict[author]['avatar']
            box_posts.ids.title_post.secondary_text = \
                posts_dict[author]['date']
            box_posts.ids.title_post.text = author
            box_posts.ids.text_posts.text = posts_dict[author]['text']
            self.ids.box_posts.add_widget(box_posts)

        app.manager.current = 'box posts'
