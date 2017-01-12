# -*- coding: utf-8 -*-
#
# plugins.py
#
# Выводит окно со списком устн=ановленных плагинов.
#

import os

from kivy.uix.rst import RstDocument

from libs.uix.dialogs import dialog, card
from libs.uix.lists import Lists


class ShowPlugin(object):
    '''Выводит на экран список установленных плагинов.'''

    def _compare_version_plugin(self, name_plugin):
        '''Сравнивает поддерживаемые плагином версии программы.'''

        app_version_min = \
            self.started_plugins[name_plugin]['app-version-min']
        app_version_max = \
            self.started_plugins[name_plugin]['app-version-max']
        app_version = \
            self.started_plugins[name_plugin]['app-version']

        if app_version_min > app_version:
            # return self.translation._(
            #    u'[color={TEXT_COLOR}]Плагин [color={LINK_COLOR}]\'{'
            #    u'NAME_PLUGIN}\'[color={TEXT_COLOR}]'
            #    u'поддерживает [color={LINK_COLOR}]Test '
            #    u'[color={TEXT_COLOR}]до версии [color={LINK_COLOR}]'
            #    u'{VERSION_MIN}. [color={TEXT_COLOR}]Ваша текущая версия - '
            #    u'[color={LINK_COLOR}]{VERSION_APP}.'
            #    u'[color={TEXT_COLOR}]Подключить?'), False
            pass
        elif app_version > app_version_max:
            # return self.translation._(
            #    u'[color={TEXT_COLOR}]Плагин [color={LINK_COLOR}]\'{'
            #    u'NAME_PLUGIN}\'[color={TEXT_COLOR}]требует '
            #    u'[color={LINK_COLOR}]Test [color={TEXT_COLOR}]'
            #    u'по крайней мере, версии [color={LINK_COLOR}]'
            #    u'{VERSION_MIN}. [color={TEXT_COLOR}]Ваша текущая версия - '
            #    u'[color={LINK_COLOR}]{VERSION_APP}. '
            #    u'[color={TEXT_COLOR}]Подключить?'), False
            pass
        else:
            return '', True

    def _save_status_plugin(self, dialog, name_plugin, result):
        if result == self.translation._(u'Да'):
            self._list_activate_plugins.append(name_plugin)
            open('{}/libs/plugins/plugins_list.list'.format(
                self.directory), 'w').write(str(self._list_activate_plugins))
        else:
            # FIXME: чекбокс не деактивируется.
            for item_list in self._list_plugins.ids.md_list.children:
                if item_list.id == name_plugin:
                    item_list.active = False
        if dialog:
            dialog.dismiss()

    def _action_plugin(self, name_plugin, state_plugin, action_plugin):
        '''Вызывается при манипуляции с пунктом плагина.
        Принимает имя, статус чекбокса ('normal/down')
        и действие ('item/check'), выбранного из списка плагина.'''

        if action_plugin == 'check':  # выбран чекбокс плагина
            if state_plugin == 'down':
                text, result = self._compare_version_plugin(name_plugin)
                if not result:
                    text = text.format(
                        TEXT_COLOR=self.text_color,
                        NAME_PLUGIN=name_plugin,
                        LINK_COLOR=self.text_link_color,
                        VERSION_MIN=self.started_plugins[name_plugin][
                            'app-version-min'],
                        VERSION_APP=self.started_plugins[name_plugin][
                            'app-version']
                    )
                    buttons = [
                        [self.translation._(u'Да'), lambda *x:
                            self._save_status_plugin(
                                window, name_plugin,
                                self.translation._(u'Да'))],
                        [self.translation._(u'Нет'), lambda *x:
                            self._save_status_plugin(
                                window, name_plugin,
                                self.translation._(u'Нет'))]
                    ]
                    window = dialog(
                        text=text, title=self.title, buttons=buttons,
                        dismiss=False
                    )
                else:
                    self._save_status_plugin(
                        None, name_plugin, self.translation._(u'Да')
                    )
            else:
                try:
                    self._list_activate_plugins.remove(name_plugin)
                    open('{}/libs/plugins/plugins_list.list'.format(
                        self.directory), 'w').write(
                            str(self._list_activate_plugins)
                    )
                except ValueError:
                    pass
        else:
            self._show_info_plugin(name_plugin)

    def _get_info_plugins(self):
        '''Возвращает словарь вида
        {'Name item': ['Desc item', 'icon_item.png'], ...}.'''

        dict_info_plugins = {}
        self._list_activate_plugins = eval(
            open('{}/libs/plugins/plugins_list.list'.format(
                self.directory)).read())

        for plugin in os.listdir('{}/libs/plugins'.format(self.directory)):
            if not os.path.isdir('{}/libs/plugins/{}'.format(
                    self.directory, plugin)):
                continue

            if plugin in self._list_activate_plugins:
                active = True
            else:
                active = False

            plugin_desc = self.started_plugins[plugin]['plugin-desc']
            plugin_icon = '{}/libs/plugins/{}/plugin_logo.png'.format(
                self.directory,
                self.started_plugins[plugin]['plugin-package']
            )

            if not os.path.exists(plugin_icon):
                plugin_icon = 'data/images/plugin_logo.png'
            dict_info_plugins[plugin] = [plugin_desc, plugin_icon, active]

        return dict_info_plugins

    def _show_info_plugin(self, name_plugin):
        '''Вызывается при клике на имя плагина из списка.'''

        if not os.path.exists('{}/libs/plugins/{}/README.rst'.format(
                self.directory, name_plugin)):
            dialog(
                text=self.translation._(u'Нет информации о плагине!'),
                title=name_plugin
            )
        else:
            info_plugin = open('{}/libs/plugins/{}/README.rst'.format(
                self.directory, name_plugin)).read()
            info_plugin = info_plugin.format(
                NAME_APP=self.title,
                VERSION=self.started_plugins[name_plugin]['plugin-version'],
                AUTHOR=self.started_plugins[name_plugin]['plugin-author'],
                MAIL=self.started_plugins[name_plugin]['plugin-mail'],
            )
            # TODO: избавиться от использования RstDocument.
            widget_info = RstDocument(
                text=info_plugin, background_color=self.alpha,
                underline_color=self.underline_rst_color
            )
            card(widget_info, size=(.75, .6))

    def show_plugins(self, *args):
        '''Выводит на экран список установленных плагинов.'''

        dict_info_plugins = self._get_info_plugins()
        if not dict_info_plugins.__len__():
            dialog(
                text=self.translation._(u'Нет установленных плагинов!'),
                title=self.title
            )
            return

        self._list_plugins = Lists(
            dict_items=dict_info_plugins,
            events_callback=self._action_plugin, flag='two_list_icon_check'
        )
        card(self._list_plugins)
