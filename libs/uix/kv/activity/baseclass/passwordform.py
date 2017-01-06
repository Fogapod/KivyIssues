from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty


class PasswordForm(BoxLayout):
    callback = ObjectProperty(lambda x: x)
