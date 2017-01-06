# -*- coding: utf-8 -*-

from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle


def canvas_add(instance, color=None, pos=(0, 0), shift=None, source=None):
    '''Добавляет canvas в объект.

    :type shift: tuple;
    :param shift: например, (2.5, 3) - сдвиг по вертикали и горизонтали,
                  когда нужно создать имитацию тени;
    '''

    with instance.canvas.before:
        if color:
            Color(rgba=color)
        if not source:
            canvas_instance = Rectangle(
                pos=pos, size=(instance.width, instance.height)
            )
        else:
            canvas_instance = Rectangle(
                pos=pos, size=(instance.width, instance.height), source=source
            )

        def on_canvas_pos(instance, value):
            if shift:
                x, y = value
                shift_x, shift_y = shift
                canvas_instance.pos = (x + shift_x, y - shift_y)
            else:
                canvas_instance.pos = value

        def on_canvas_size(instance, value):
            canvas_instance.size = value

        instance.bind(size=on_canvas_size, pos=on_canvas_pos)
