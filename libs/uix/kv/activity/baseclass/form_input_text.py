from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty


class FormInputText(BoxLayout):
    callback = ObjectProperty(lambda x: x)

    def clear(self):
        self.ids.text_input.text = ''
        self.ids.text_input.message = ''
