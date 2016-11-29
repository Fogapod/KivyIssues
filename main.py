#! /usr/bin/python3.4
# -*- coding: utf-8 -*-
#
# main.py
#
# Точка входа в приложение. Запускает основной программный код program.py.
# В случае ошибки, выводит на экран окно с ее текстом.
#

import os
import sys
import traceback

sys.dont_write_bytecode = True
directory = os.path.split(os.path.abspath(sys.argv[0]))[0]

try:
    import webbrowser
    import six.moves.urllib

    import kivy
    kivy.require('1.9.1')

    from kivy.base import runTouchApp
    from kivy.config import Config

    # Указываем пользоваться системным методом ввода, использующимся на
    # платформе, в которой запущенно приложение.
    Config.set('kivy', 'keyboard_mode', 'system')
    Config.set('graphics', 'width', '350')
    Config.set('graphics', 'height', '600')

    # Activity баг репорта.
    from libs.uix.kv.activity.baseclass.bugreporter import BugReporter
except Exception:
    traceback.print_exc(file=open('{}/error.log'.format(directory), 'w'))
    sys.exit(1)


__version__ = '0.0.1'


def main():
    app = None

    try:
        from libs.loadplugin import load_plugin  # загрузка плагинов
        from program import Program  # основной класс программы

        # Запуск приложения.
        app = Program()
        load_plugin(app)
        app.run()
    except Exception:
        text_error = traceback.format_exc()
        open('{}/error.log'.format(directory), 'w').write(text_error)
        print(text_error)

        if app:  # очищаем экран приложения от всех виджетов
            try:
                app.stop()
            except AttributeError:
                pass

        def callback_report(*args):
            '''Функция отправки баг-репорта'''

            try:
                txt = six.moves.urllib.parse.quote(
                    report.txt_traceback.text.encode('utf-8')
                )
                url = 'https://github.com/HeaTTheatR/KivyIssues/issues' \
                      '/new?body=' + txt
                webbrowser.open(url)
            except Exception:
                sys.exit(1)

        report = BugReporter(
            callback_report=callback_report, txt_report=text_error,
            icon_background='data/images/logo.png'
        )
        runTouchApp(report)


if __name__ in ('__main__', '__android__'):
    main()
