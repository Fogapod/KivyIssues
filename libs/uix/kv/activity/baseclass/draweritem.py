from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty


class DrawerItem(BoxLayout):
    icon = StringProperty('vector-circle')
    text = StringProperty()
    callback = ObjectProperty(lambda: None)
