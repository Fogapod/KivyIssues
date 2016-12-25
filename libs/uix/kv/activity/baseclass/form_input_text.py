from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty


class FormInputText(BoxLayout):
    callback = ObjectProperty(lambda x: None)
