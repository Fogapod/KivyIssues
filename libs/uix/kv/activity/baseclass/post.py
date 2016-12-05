from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

from libs.programclass.showposts import ShowPosts


class Post(BoxLayout):
    _app = ObjectProperty()

    def tap_on_text_or_link_post(self, *args):
        instanse_label = args[0][0]
        post_id, count_comment = instanse_label.id.split('-')
        ShowPosts(app=self._app, count_comment=count_comment,
                  post_id=post_id, comments=True).show_posts()
