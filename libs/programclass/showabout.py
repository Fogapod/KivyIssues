# -*- coding: utf-8 -*-
#
# about.py
#
# Выводит окно с информацией о приложении.
#

from libs.uix.dialogs import dialog


class ShowAbout(object):

    def show_about(self, *args):
        dialog(
            text=self.translation._(u'Версия - 0.0.1'))

    def _callback(self, instance, text_link):
        print(instance, text_link)
