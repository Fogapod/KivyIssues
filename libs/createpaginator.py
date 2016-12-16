# -*- coding: utf-8 -*-

from libs.paginator import paginator


def create_paginator(number_posts=1, current_number_page=1, pages=20,
                     link_color='5d86cc', number_color='000000'):
    '''Формирует нумерацию страниц и помечает выбраную.

    :param current_number_page: номер текущей страницы;
    :param number_posts: количество записей;
    :param pages: количество записей на одной странице;

    '''

    number_pages = int(round(number_posts / pages))
    if not number_pages:
            number_pages = 1
    list_pages = paginator(number_pages, current_number_page)

    build_pages = ""
    for number_page in list_pages:
        try:
            number_page = int(number_page.replace("[", "").replace("]", ""))

            if current_number_page == number_page:
                color = link_color
            else:
                color = number_color
        except ValueError:
            color = link_color

        build_pages += \
            '[color={}][ref={number_page}]{number_page}[/ref] '.format(
                color, number_page=number_page)

    return build_pages
