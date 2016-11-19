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

    def get_info_from_post(self, count_issues):
        '''
        :type count_issues: str;
        :param count_issues: количество получаемых постов;

        Возвращает словарь:
        {'Имя атора поста':
            {'text': 'Текст поста', 'date': '2016-11-14 16:21:20',
             'attachments': ['', 'https://p.vk.me/c9/v60/36fe/ylDQ.jpg', ...],
             'avatar': 'https://pp.vk.me/c17/v6760/1/FdjA4ho.jpg',
             'comments': 4}, ...
        }

        '''

        wall_posts, info = vkr.get_issues(offset='0', count=count_issues)

        posts_dict = {}
        attachments_list = []

        for i, data_post in enumerate(wall_posts['profiles']):
            post_dict = {}
            author_id = data_post['id']
            avatar = data_post['photo_50']
            first_name = data_post['first_name']
            last_name = data_post['last_name']
            if self.data.PY2:
                author = u'{} {}'.format(first_name, last_name)
            else:
                author = '{} {}'.format(first_name, last_name)
            post_dict['avatar'] = avatar

            for data_post in wall_posts['items']:
                if data_post['from_id'] == author_id:
                    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                        data_post['date']
                        )
                    )
                    text = self.mark_links_in_post(data_post['text'])
                    comments = data_post['comments']['count']

                    post_dict['date'] = date
                    post_dict['text'] = text
                    post_dict['comments'] = comments

                    if 'attachments' in data_post:
                        attachments_dict = data_post['attachments']
                        for attachments_data in attachments_dict:
                            if attachments_data['type'] == 'photo':
                                title_attachments = \
                                    attachments_data['photo']['text']
                                url_attachments = \
                                    attachments_data['photo']['photo_130']
                                attachments_list.append(title_attachments)
                                attachments_list.append(url_attachments)
                                post_dict['attachments'] = attachments_list
                        attachments_list = []
            posts_dict[author] = post_dict

        return posts_dict
