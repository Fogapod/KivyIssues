# -*- coding: utf-8 -*-

import requests as r
import time
import re

from libs import vk

__author__ = 'Eugene Ershov - http://vk.com/fogapod'

GROUP_ID = '99411738'
MGROUP_ID = '-99411738'

api = None


def vk_request_errors(request):
    def request_errors(*args, **kwargs):
        # response = request(*args, **kwargs); time.sleep(0.66) 
        # Для вывода ошибки в консоль
        try:
            response = request(*args, **kwargs)
        except Exception as e:
            if 'Too many requests per second.' in str(e):
                time.sleep(0.66)
                return request_errors(*args, **kwargs)
            elif 'Failed to establish a new connection' in str(e) != -1:
                print('Check your connection')
            elif str(e) == 'Authorization error (incorrect password)':
                print('Incorrect password!')
            elif 'Failed loading' in str(e):
                raise
            elif str(e) == 'Authorization error (captcha)':
                print('Captcha!')
            else:
                if not api:
                    print('Authentication required')
                else:
                    print('\nERROR! ' + str(e) + '\n')
            return False, str(e)
        else:
            return response, True
    return request_errors


@vk_request_errors
def log_in(**kwargs):
    # TODO: получить токен.
    """
    :login:
    :password:
    :token:

    returns True if succeed
    else returns False
    """
    global api
    scope = '204804'
    # 65536 -- offline permission; 8192 -- wall permission; 131072 -- docs
    # permission; 4 -- photos permission
    app_id = '5720412'

    token = kwargs.get('token')
    if token:
        session = vk.Session(
            access_token=token, scope=scope, app_id=app_id
        )
    else:
        login, password = kwargs.values()#['login'], kwargs['password']
        session = vk.AuthSession(
            user_login=login, user_password=password,
            scope=scope, app_id=app_id
        )

    api = vk.API(session, v='5.6')
    api.stats.trackVisitor()

    return True


@vk_request_errors
def get_members_count():
    """
    returns string if succeed
    else returns False
    """
    return api.execute.GetMembersCount()


@vk_request_errors
def get_issues(**kwargs):
    """
    :offset:
    :post_count:

    returns dict with wall posts if succeed
    else returns False
    """

    if len(args) == 2:
        offset, post_count = args
    else:
        offset = args
        post_count = '30'

    return api.wall.get(
        owner_id=MGROUP_ID, filter='others', extended='1',
        offset=offset, count=post_count
    )


@vk_request_errors
def get_issue_count():
    return api.execute.GetIssueCount()


@vk_request_errors
def send_issue(*args):
    """
    args: issue_data {'file','image','theme','issue'}

    returns string ( post id ) if succeed
    else returns False
    """
    issue_data = args[0]
    file_path = issue_data['file']
    image_path = issue_data['image']
    theme_text = issue_data['theme']
    issue_text = issue_data['issue']

    attachments = []

    doc = attach_doc(file_path)[0]
    pic = attach_pic(image_path)[0]

    if doc:
        attachments.append('doc' + str(doc[0]['owner_id'])
                           + '_' + str(doc[0]['id'])
                           )
    if pic:
        attachments.append('photo' + str(pic[0]['owner_id'])
                           + '_' + str(pic[0]['id'])
                           )

    return api.wall.post(
        owner_id=MGROUP_ID, message=theme_text
        + '\n\n' + issue_text, attachments=attachments
    )


@vk_request_errors
def get_comments(*args):
    """
    args: post_id ( requied ), offset ( required, but not throws an exception
    if not declared, default=() ), comment_count ( optional, default='100' )
    returns dict with comments if succeed else returns False
    """
    if len(args) == 3:
        post_id, offset, comment_count = args
    else:
        post_id, offset = args
        comment_count = '100'

    return api.wall.getComments(
        owner_id=MGROUP_ID, post_id=post_id,
        offset=offset, count=comment_count
    )


@vk_request_errors
def get_user_name():
    """
    returns string (First_name Last_name) if succeed
    else returns False
    """
    response = api.users.get()[0]

    return response['first_name'] + ' ' + response['last_name']


@vk_request_errors
def get_user_photo(*args):
    """
    args: photo_size ( optional ), default = 'photo_big', can be:
    'photo_medium', 'photo_small', 'photo_max' (super tiny photo)

    returns Photo if succeed
    # returns None if user have no avatar
    else returns False
    """
    if len(args) == 1:
        photo_size = args[0]
    else:
        photo_size = 'photo_big'
    url = api.users.get(fields=photo_size)[0]

    # !always returns photo!
    if 'images/question_c.gif' not in url[photo_size]:
        return r.get(url[photo_size]).content


@vk_request_errors
def attach_doc(*args):
    """
    args: path ( required )

    returns array with doc object
    else returns False
    """
    path = args[0]

    if path:
        upload_data = api.docs.getUploadServer()

        doc = {'file': open(path, 'rb')}

        response = r.post(upload_data['upload_url'], files=doc)
        json_data = response.json()

        if 'error' in json_data:
            raise Exception('Failed loading document')

        return api.docs.save(title=re.match(
            '/.+$', path), file=json_data['file']
        )


@vk_request_errors
def attach_pic(*args):
    """
    args: path ( required )

    returns array with picture object
    else returns False
    """
    path = args[0]

    if path:
        upload_data = api.photos.getWallUploadServer(group_id=GROUP_ID)

        pic = {'photo': open(path, 'rb')}

        response = r.post(upload_data['upload_url'], files=pic)
        json_data = response.json()

        if json_data['photo'] == '[]':
            raise Exception('Failed loading picture')

        return api.photos.saveWallPhoto(
            group_id=GROUP_ID, photo=json_data['photo'],
            server=json_data['server'], hash=json_data['hash']
        )
