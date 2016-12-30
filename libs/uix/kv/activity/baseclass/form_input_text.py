from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty, ObjectProperty


class FormInputText(BoxLayout):
    button_text_send = StringProperty()
    label_color = ListProperty()
    label_text_to = StringProperty()
    avatar_icon = StringProperty()
    add_file_icon = StringProperty()
    add_foto_icon = StringProperty()
    delete_whom_icon = StringProperty()
    callback = ObjectProperty(lambda x: None)
    background_color = ListProperty(
        [0.9686274509803922, 0.9686274509803922, 0.9686274509803922, 1]
    )

'''
        theme_cls = ThemeManager()
        theme_cls.primary_palette = 'BlueGrey'

        Builder.load_string(activity)

        form = FormInputText()
        form.ids.text_input.background_normal = 'text_input.png'
        form.avatar_icon = 'data/logo/kivy-icon-64.png'
        form.add_file_icon = 'paperclip.png'
        form.add_foto_icon = 'camera.png'
        form.label_color = theme_cls.primary_color
        form.label_text_send = 'Отправить'
        form.label_text_to = 'Глеб'
        form.callback = callback

        return form
'''