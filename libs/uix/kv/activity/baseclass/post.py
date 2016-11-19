from kivy.uix.boxlayout import BoxLayout


class Post(BoxLayout):

    def on_enter(self):
        app = self.manager._app
