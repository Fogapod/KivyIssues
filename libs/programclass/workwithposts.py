# -*- coding: utf-8 -*-

from kivy.logger import PY2

from libs.vkrequests import get_issues, get_comments


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

        mark_text = self.PATTERN_REPLACE_LINK.sub(replace, post)

        return mark_text

    def get_info_from_post(self, count_issues, post_id='', comments=False):
        '''
        :type count_issues: str;
        :param count_issues: количество получаемых постов;
        :param post_id: id поста для которого получаем комментарии;
        :param comments: если True -получаем комментарии;

        Возвращает словарь:
        {'Имя атора поста':
            {'text': 'Текст поста', 'date': '2016-11-14 16:21:20',
             'attachments': ['', 'https://p.vk.me/c9/v60/36fe/ylDQ.jpg', ...],
             'avatar': 'https://pp.vk.me/c17/v6760/1/FdjA4ho.jpg',
             'comments': 4}, ...
        }

        '''

        if not comments:
            wall_posts, text_error = get_issues(offset=0, count=count_issues)
        else:
            wall_posts, text_error = get_comments(id=post_id, count=count_issues)

        profiles_dict = {}

        if not wall_posts:
            print(text_error)
            return

        for data_post in wall_posts['profiles']:
            post_dict = {}
            first_name = data_post['first_name']
            last_name = data_post['last_name']
            author_online = data_post['online']

            if PY2:
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
