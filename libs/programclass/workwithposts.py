# -*- coding: utf-8 -*-

import time

from libs import vkrequests as vkr


class WorkWithPosts(object):

    def mark_links_in_post(self, post, link_color='78a5a3ff'):
        '''Находит в тексте поста ссылки и маркирует их согласно
        форматированию ссылок в Kivy.

        '''

        def replace(mo):
            if mo:
                link = mo.group()
                marker = \
                    '[ref={}][color={}]{}[/color][/ref]'.format(
                        link, link_color, link
                    )

                return marker

        mark_text = self.data.pattern_replace_link.sub(replace, post)

        return mark_text

    def get_info_from_post(self, count_issues='20', offset='0'):
        '''
        :type count_issues: str;
        :param count_issues: количество получаемых постов;
        :param only_questions: все или только свои посты;

        Возвращает словарь:
        {id атора поста:
            {'author_name': 'Имя автора поста',
             'avatar': 'https://pp.vk.me/c17/v6760/1/FdjA4ho.jpg',}, ...
        }

        и список словарей с информацией о постах группы, возврвщаемый
        функцией get_issues.

        '''

        wall_posts, info = vkr.get_issues(offset=offset, count=count_issues)
        profiles_dict = {}

        if not wall_posts:
            print(info)
            return

        for data_post in wall_posts['profiles']:
            post_dict = {}
            first_name = data_post['first_name']
            last_name = data_post['last_name']
            author_online = data_post['online']

            if self.data.PY2:
                author_name = u'{} {}'.format(first_name, last_name)
            else:
                author_name = '{} {}'.format(first_name, last_name)

            post_dict['avatar'] = data_post['photo_100']
            post_dict['author_name'] = author_name
            post_dict['author_online'] = author_online

            if author_online:
                if 'online_mobile' in data_post:
                    post_dict['device'] = 'mobile'
                else:
                    post_dict['device'] = 'computer'

            profiles_dict[data_post['id']] = post_dict

        return profiles_dict, wall_posts['items']
