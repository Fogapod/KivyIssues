from kivy.uix.boxlayout import BoxLayout


class Post(BoxLayout):

    def on_enter(self):
        app = self.manager._app

    def tap_text_or_link(self, *args):
        print(args)
