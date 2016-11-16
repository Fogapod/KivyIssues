# -*- coding: utf-8 -*-

import requests as r
import time
import re

from libs import vk

__author__ = 'Eugene Ershov - http://vk.com/fogapod'

GROUP_ID = '99411738'

api = None


def vk_request_errors(REQUEST):
    def request_errors(*args, **kwargs):
        # RESPONSE = REQUEST(*args, **kwargs)  # Для вывода ошибки в консоль
        try:
            RESPONSE = REQUEST(*args, **kwargs)
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
            return RESPONSE, True
    return request_errors


@vk_request_errors
def log_in(**kwargs):
    # TODO: получить токен.
    """
    args: LOGIN ( required ), PASSWORD ( required )
    returns True if succeed
    else returns False
    """
    global api
    scope = '204804'
    # 65536 -- offline permission; 8192 -- wall permission; 131072 -- docs
    # permission; 4 -- photos permission
    app_id = '5720412'
    if 'token' in kwargs:
        token = kwargs['token']
        session = vk.Session(
            access_token=token, scope=scope, app_id=app_id
        )
    else:
        login, password = kwargs['login'], kwargs['password']
        session = vk.AuthSession(
            user_login=login, user_password=password,
            scope=scope, app_id=app_id
        )
    api = vk.API(session, v='5.6')
    api.stats.trackVisitor()
    return True


@vk_request_errors
def get_members_count(*args):
    """
    args: None
    returns string if succeed
    else returns False
    """

    RESPONSE = api.groups.getById(
        group_id=GROUP_ID,
        fields='members_count')
    return RESPONSE[0]['members_count']


@vk_request_errors
def get_issues(*args):
    """
    args: OFFSET ( required, but not throws an exception if not declared,
    default=() ), POST_COUNT ( optional, default='30' )
    returns dict with wall posts if succeed
    else returns False
    """

    if len(args) == 2:
        OFFSET, POST_COUNT = args
    else:
        OFFSET = args
        POST_COUNT = '30'
    # запись со смайликами: 23 (offset='22')
    return api.wall.get(
        owner_id='-' + GROUP_ID, filter='others', extended='1',
        offset=OFFSET, count=POST_COUNT
    )


@vk_request_errors
def get_issue_count(*args):
    return api.execute.GetIssueCount()


@vk_request_errors
def send_issue(*args):
    """
    args: ISSUE_DATA {'file','image','theme','issue'}

    returns string ( post id ) if succeed
    else returns False
    """
    ISSUE_DATA = args[0]
    FILE = ISSUE_DATA['file']
    IMAGE = ISSUE_DATA['image']
    THEME = ISSUE_DATA['theme']
    ISSUE = ISSUE_DATA['issue']

    ATTACHMENTS = []

    DOC = attach_doc(FILE)[0]
    PIC = attach_pic(IMAGE)[0]

    if DOC:
        ATTACHMENTS.append('doc' +
                           str(DOC[0]['owner_id']) +
                           '_' +
                           str(DOC[0]['id']))
    if PIC:
        ATTACHMENTS.append('photo' +
                           str(PIC[0]['owner_id']) +
                           '_' +
                           str(PIC[0]['id']))

    return api.wall.post(
        owner_id='-' + GROUP_ID, message=THEME + '\n\n' + ISSUE,
        attachments=ATTACHMENTS
    )


@vk_request_errors
def get_comments(*args):
    """
    args: POST_ID ( requied ), OFFSET ( required, but not throws an exception
    if not declared, default=() ), COMMENT_COUNT ( optional, default='100' )
    returns dict with comments if succeed else returns False
    """

    if len(args) == 3:
        POST_ID, OFFSET, COMMENT_COUNT = args
    else:
        POST_ID, OFFSET = args
        COMMENT_COUNT = '100'
    return api.wall.getComments(
        owner_id='-' + GROUP_ID, post_id=POST_ID, offset=OFFSET,
        count=COMMENT_COUNT
    )


@vk_request_errors
def get_user_name(*args):
    """
    args: None
    returns string (First_name Last_name) if succeed
    else returns False
    """
    RESPONSE = api.users.get()[0]
    return RESPONSE['first_name'] + ' ' + RESPONSE['last_name']


@vk_request_errors
def get_user_photo(*args):
    """
    args: PHOTO_SIZE ( optional ), default = 'photo_big', can be:
    'photo_medium', 'photo_small', 'photo_max' (super tiny photo)
    returns Photo if succeed
    # returns None if user have no avatar
    else returns False
    """

    if len(args) == 1:
        PHOTO_SIZE = args[0]
    else:
        PHOTO_SIZE = 'photo_big'
    url = api.users.get(fields=PHOTO_SIZE)[0]
    # !always returns photo!
    if 'images/question_c.gif' not in url[PHOTO_SIZE]:
        return r.get(url[PHOTO_SIZE]).content


# processing ATTACHMENTS in send_issue
# WIP

@vk_request_errors
def attach_doc(*args):
    """
    args: PATH ( required )

    returns array with doc object
    else returns False
    """
    PATH = args[0]

    if PATH:
        UPLOAD_DATA = api.docs.getUploadServer()
        DOC = {'file': open(PATH, 'rb')}
        UPLOADED = r.post(UPLOAD_DATA['upload_url'], files=DOC)
        JSON_DATA = UPLOADED.json()

        if 'error' in JSON_DATA:
            raise Exception('Failed loading document')

        return api.docs.save(
            title=re.match('/.+$', PATH), file=JSON_DATA['file']
        )


@vk_request_errors
def attach_pic(*args):
    """
    args: PATH ( required )

    returns array with picture object
    else returns False
    """
    PATH = args[0]

    if PATH:
        UPLOAD_DATA = api.photos.getWallUploadServer(
            group_id=GROUP_ID)
        PHOTO = {'photo': open(PATH, 'rb')}
        UPLOADED = r.post(UPLOAD_DATA['upload_url'], files=PHOTO)
        JSON_DATA = UPLOADED.json()

        if JSON_DATA['photo'] == '[]':
            raise Exception('Failed loading picture')

        return api.photos.saveWallPhoto(
            group_id=GROUP_ID, photo=JSON_DATA['photo'],
            server=JSON_DATA['server'], hash=JSON_DATA['hash']
        )
