# -*- coding: utf-8 -*-
#
# Выводит экран с текстом лицензии.
#

import os

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

from libs.uix.dialogs import dialog
libs/uix/kv/activity/baseclass/license.py

class ShowLicense(Screen):

    _app = ObjectProperty()


