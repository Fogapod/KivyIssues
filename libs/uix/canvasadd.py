# -*- coding: utf-8 -*-

from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle


def canvas_add(instance, color=None, pos=(0, 0), shift=None):
    '''Добавляет canvas в объект.

    :type shift: tuple;
    :param shift: например, (2.5, 3) - сдвиг по вертикали и горизонтали,
                  когда нужно создать имитацию тени;
    '''

    if not color:
        color = [0, 0, 0, 1]

    with instance.canvas.before:
        Color(rgba=color)
        canvas_instance = Rectangle(
            pos=pos, size=(instance.width, instance.height)
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
