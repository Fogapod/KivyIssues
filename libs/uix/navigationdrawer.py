# -*- coding: utf-8 -*-

from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.elevationbehavior import ElevationBehavior
from kivymd.slidingpanel import SlidingPanel
from kivymd.theming import ThemableBehavior

Builder.load_string('''
#: import Toolbar kivymd.toolbar.Toolbar

<NavDrawerToolbar@Toolbar>
    canvas:
        Color:
            rgba: root.theme_cls.divider_color
        Line:
            points: self.x, self.y, self.x+self.width,self.y

<NavigationDrawer>
    _list: list
    elevation: 0
    canvas:
        Color:
            rgba: root.theme_cls.bg_light
        Rectangle:
            size: root.size
            pos: root.pos
    NavDrawerToolbar:
        title: root.title
        opposite_colors: False
        title_theme_color: 'Secondary'
        background_color: root.theme_cls.bg_light
        elevation: 0
''')


class NavigationDrawer(SlidingPanel, ThemableBehavior, ElevationBehavior):
    title = StringProperty()

    def _get_main_animation(self, duration, t, x, is_closing):
        a = super(NavigationDrawer, self)._get_main_animation(
            duration, t, x, is_closing
        )
        a &= Animation(
            elevation=0 if is_closing else 5, t=t, duration=duration
        )
        return a
