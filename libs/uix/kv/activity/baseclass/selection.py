from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty


class Selection(BoxLayout):
    text = StringProperty()
    callback = ObjectProperty()
