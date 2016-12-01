from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty


class Post(BoxLayout):
    _app = ObjectProperty()

    def tap_on_text_or_link_post(self, *args):
        instanse_label = args[0][0]
        self._app.open_dialog(
            text='Your tap on post with id - {}'.format(instanse_label.id),
            dismiss=True
        )
