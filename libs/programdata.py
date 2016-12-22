# -*- coding: utf-8 -*-
#
# programdata.py
#

import os
import sys
import re
import ast
import traceback
import threading

from kivy.config import ConfigParser
from kivy.logger import PY2
from kivy.utils import get_color_from_hex


def thread(func):
    def execute(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs).start()

    return execute


if PY2:
    select_locale = {u'Русский': 'russian', 'English': 'english'}
else:
    select_locale = {'Русский': 'russian', 'English': 'english'}

prog_path = os.path.split(os.path.abspath(sys.argv[0]))[0]

# Если файл настроек отсутствует.
if not os.path.exists('{}/program.ini'.format(prog_path)):
    if PY2:
        language = u'Русский'
    else:
        language = 'Русский'
    theme = 'default'
    authorization = False
    regdata = {'login': None, 'password': None}
    user_name = 'User'
    issues_in_group = 0
    count_issues = 20
else:
    config = ConfigParser()
    config.read('{}/program.ini'.format(prog_path))
    theme = config.get('General', 'theme')
    language = config.get('General', 'language')
    authorization = config.getint('General', 'authorization')
    regdata = ast.literal_eval(config.get('General', 'regdata'))
    user_name = config.get('General', 'user_name')
    issues_in_group = config.getint('General', 'issues_in_group')
    count_issues = config.getint('General', 'count_issues')

old_language = language
language = select_locale[language]

# -----------------------УСТАНОВКА ЦВЕТОВОЙ ТЕМЫ---------------------------
config_theme = ConfigParser()
config_theme.read('{}/data/themes/{theme}/{theme}.ini'.format(
    prog_path, theme=theme))

alpha = \
    get_color_from_hex(config_theme.get('color', 'alpha'))
list_color = \
    get_color_from_hex(config_theme.get('color', 'list_color'))
text_color_from_hex = \
    get_color_from_hex(config_theme.get('color', 'text_color'))
floating_button_down_color = \
    get_color_from_hex(config_theme.get(
        'color', 'floating_button_down_color')
    )
floating_button_disabled_color = \
    get_color_from_hex(config_theme.get(
        'color', 'floating_button_disabled_color')
    )

text_color = config_theme.get('color', 'text_color')
underline_rst_color = config_theme.get('color', 'underline_rst_color')
text_key_color = config_theme.get('color', 'text_key_color')
text_link_color = config_theme.get('color', 'text_link_color')

try:  # устанавливаем языковую локализацию
    if not PY2:
        exec(
            open('{}/data/language/{}.txt'.format(
                prog_path, language), encoding='utf-8-sig').read()
        )
    else:
        exec(
            open('{}/data/language/{}.txt'.format(prog_path, language)).read()
        )
except Exception:
    raise Exception(traceback.format_exc())

dict_language = {
    string_lang_on_russian: 'russian',
    string_lang_on_english: 'english'
}

name_banners = os.listdir('{}/data/images/banners'.format(prog_path))

possible_files = {
    string_lang_add_image: [['.png', '.jpg', '.jpeg', '.gif'], string_lang_wrong_image],
    string_lang_add_file: [['.zip', '.txt'], string_lang_wrong_file]
}

menu_items = [string_lang_current_password, string_lang_new_password]

device_online = {
    'mobile': 'data/images/mobile.png',
    'computer': 'data/images/computer.png',
    0: 'data/images/offline.png'
}

pattern_whom_comment = re.compile(r'\[id\d+\|\w+\]', re.UNICODE)
pattern_replace_link = re.compile(r'(?#Protocol)(?:(?:ht|f)tp(' \
                             '?:s?)\:\/\/|~\/|\/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:\/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|\/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,'
                                  '*:=]|%[a-f\d]{2})*)?')
