import os
import pickle

from kivy.clock import Clock


class IssueForm(object):

    def clear_form(self):
        instance_add_image = self.screen.ids.ask_a_question.ids.add_image
        instance_add_file = self.screen.ids.ask_a_question.ids.add_file
        instance_add_image.ids.label.text = self.data.string_lang_add_image
        instance_add_file.ids.label.text = self.data.string_lang_add_file
        instance_add_image.ids.check.active = False
        instance_add_file.ids.check.active = False
        self.screen.ids.ask_a_question.ids.theme_field.text = ''
        self.screen.ids.ask_a_question.ids.issue_field.text = ''

    def restore_form(self):
        def set_focus_on_textfield(interval=0, instance_textfield=None,
                                   focus=False):
            if instance_textfield:
                instance_textfield.focus = focus

        instance_add_image = self.screen.ids.ask_a_question.ids.add_image
        instance_add_file = self.screen.ids.ask_a_question.ids.add_file
        path_to_attach_image = self.saved_form['image']
        path_to_attach_file = self.saved_form['file']

        if path_to_attach_image:
            instance_add_image.ids.label.text = \
                os.path.split(path_to_attach_image)[1]
            instance_add_image.ids.check.active = True
        else:
            instance_add_image.ids.label.text = self.data.string_lang_add_image
        if path_to_attach_file:
            instance_add_file.ids.label.text = \
                os.path.split(path_to_attach_file)[1]
            instance_add_file.ids.check.active = True
        else:
            instance_add_file.ids.label.text = self.data.string_lang_add_file

        self.screen.ids.ask_a_question.ids.theme_field.focus = True
        self.screen.ids.ask_a_question.ids.theme_field.text = \
            self.saved_form['theme']
        Clock.schedule_once(lambda x: set_focus_on_textfield(
            instance_textfield=self.screen.ids.ask_a_question.ids.theme_field),
            .5)

        self.screen.ids.ask_a_question.ids.issue_field.text = \
            self.saved_form['issue']
        Clock.schedule_once(lambda x: set_focus_on_textfield(
            instance_textfield=self.screen.ids.ask_a_question.ids.issue_field,
            focus=True), .5)

    def create_data_from_form(self):
        name_adding_file = \
            self.manager.current_screen.ids.add_file.ids.label.text
        name_adding_image = \
            self.manager.current_screen.ids.add_image.ids.label.text

        if name_adding_file == self.data.string_lang_add_file:
            _file = None
        else:
            _file = '{}/{}'.format(
                self.manager.current_screen.ids.add_file.path_to_file,
                name_adding_file
            )
        if name_adding_image == self.data.string_lang_add_image:
            _image = None
        else:
            _image = '{}/{}'.format(
                self.manager.current_screen.ids.add_image.path_to_file,
                name_adding_image
            )

        return {
            'file': _file, 'image': _image,
            'theme': self.manager.current_screen.ids.theme_field.text,
            'issue': self.manager.current_screen.ids.issue_field.text
        }

    def clear_data(self):
        self.save_form()
        self.read_form()

    def save_form(self, data=None):
        if not data:
            data = {}
        with open('{}/data/issues/issues.ini'.format(
                self.directory), 'wb') as file_issue:
            pickle.dump(data, file_issue)

    def read_form(self):
        with open('{}/data/issues/issues.ini'.format(
                self.directory), 'rb') as file_issue:
            issue_data = pickle.load(file_issue)
        return issue_data if issue_data.__len__() else None

    def check_existence_issues(self):
        if not os.path.exists('{}/data/issues'.format(self.directory)):
            os.mkdir('{}/data/issues'.format(self.directory))
        if not os.path.exists(
                '{}/data/issues/issues.ini'.format(self.directory)):
            self.save_form()
