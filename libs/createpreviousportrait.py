# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw


def prepare_mask(size, antialias=2):
    '''Подготавливает маску, рисуя её в <antialias>.'''

    mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)


def crop(im, s):
    '''Обрезает и масштабирует изображение под заданный размер.'''

    w, h = im.size
    k = w // s[0] - h // s[1]
    if k > 0:
        im = im.crop(((w - h) // 2, 0, (w + h) // 2, h))
    elif k < 0:
        im = im.crop((0, (h - w) // 2, w, (h + w) // 2))
    return im.resize(s, Image.ANTIALIAS)


def create_previous_portrait(path_to_image, path_to_new_image,
                             size=(200, 200)):
    im = Image.open(path_to_image)
    im = crop(im, size)
    im.putalpha(prepare_mask(size, 4))
    im.save(path_to_new_image)
