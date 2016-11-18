# -*- coding: utf-8 -*-

import requests as r
import time
import re

from libs import vk

__author__ = 'Eugene Ershov - http://vk.com/fogapod'

GROUP_ID = '99411738'
MGROUP_ID = '-' + GROUP_ID

api = None
token = None


def vk_request_errors(request):
    def request_errors(*args, **kwargs):
        # response = request(*args, **kwargs); time.sleep(0.66)
        # Для вывода ошибки в консоль
        try:
            response = request(*args, **kwargs)
        except Exception as e:
            if 'Too many requests per second' in str(e):
                time.sleep(0.66)
                return request_errors(*args, **kwargs)

            elif 'Failed to establish a new connection'in str(e):
                print('Check your connection')

            elif str(e) == 'Authorization error (incorrect password)':
                print('Incorrect password!')

            elif 'Failed loading' in str(e):
                raise

            elif 'Failed receiving session' in str(e):
                print('Error receiving session!')

            elif 'Auth check code is needed' in str(e):
                print('Auth code is needed!')

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
    # vk.logger.setLevel('DEBUG')
    """
    :token:
    :key:
    :login:
    :password:
    """
    scope = '204804'
    # 65536 -- offline; 8192 -- wall; 131072 -- docs; 4 -- photos
    app_id = '5720412'

    global token
    token = kwargs.get('token')
    key = kwargs.get('key')

    if token:
        session = vk.Session(
            access_token=token, scope=scope, app_id=app_id
        )
    elif key:
        login, password = kwargs['login'], kwargs['password']
        # TODO
        # session = vk.AuthSession(
        #    user_login=login, client_secret=key,
        #    user_password=password, scope=scope,
        #    grant_type=password, app_id=app_id
        #)
    else:
        login, password = kwargs['login'], kwargs['password']
        session = vk.AuthSession(
            user_login=login, user_password=password,
            scope=scope, app_id=app_id
        )

    global api
    try:
        api = vk.API(session, v='5.6')
    except UnboundLocalError:
        raise Exception('Failed receiving session!')

    api.stats.trackVisitor()

    return True


@vk_request_errors
def get_members_count():
    """
    returns string
    """
    return api.execute.GetMembersCount(gid=GROUP_ID)


@vk_request_errors
def get_user_name():
    """
    returns string (First_name Last_name)
    """
    return api.execute.GetUserName()


@vk_request_errors
def get_issue_count():
    return api.execute.GetIssuesCount(mgid=MGROUP_ID)


@vk_request_errors
def get_issues(**kwargs):
    # TODO упорядочить получаемые данные через хранимые процедуры
    """
    :offset: ( '0' )
    :count: ( '30' )

    returns dict
    """
    offset = kwargs.get('offset', '0')
    post_count = kwargs.get('count', '30')

    return api.wall.get(
        owner_id=MGROUP_ID, filter='others', extended='1',
        offset=offset, count=post_count
    )


@vk_request_errors
def send_issue(*args):
    """
    :issue_data: ( {'file','image','theme','issue'} )

    returns string ( post id )
    """
    issue_data = args[0]
    path_to_file = issue_data['file']
    path_to_image = issue_data['image']
    theme_text = issue_data['theme']
    issue_text = issue_data['issue']

    attachments = []

    doc = attach_doc(path=path_to_file)[0]
    pic = attach_pic(path=path_to_image)[0]

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
def attach_doc(**kwargs):
    """
    :path:

    returns array with doc object
    """
    path = kwargs['path']

    if path:
        upload_data = api.docs.getUploadServer()

        doc = {'file': open(path, 'rb')}

        response = r.post(upload_data['upload_url'], files=doc)
        json_data = response.json()

        if 'error' in json_data:
            raise Exception('Failed loading document')

        try:
            return api.docs.save(title=re.match(
                '/.+$', path), file=json_data['file']
            )
        except:
            raise Exception('Failed loading document')


@vk_request_errors
def attach_pic(**kwargs):
    """
    :path:

    returns array with pic object
    """
    path = kwargs['path']

    if path:
        upload_data = api.photos.getWallUploadServer(group_id=GROUP_ID)

        pic = {'photo': open(path, 'rb')}

        response = r.post(upload_data['upload_url'], files=pic)
        json_data = response.json()

        if json_data['photo'] == '[]':
            raise Exception('Failed loading picture')

        try:
            return api.photos.saveWallPhoto(
                group_id=GROUP_ID, photo=json_data['photo'],
                server=json_data['server'], hash=json_data['hash']
            )
        except:
            raise Exception('Failed loading picture')


@vk_request_errors
def get_comments(**kwargs):
    # TODO упорядочить получаемые данные через хранимые процедуры
    """
    :post_id:
    :offset: ( '0' )
    :count: ( '100' )

    returns dict with comments
    """
    post_id = kwargs['id']
    offset = kwargs.get('offset', '0')
    comment_count = kwargs.get('count', '100')

    return api.wall.getComments(
        owner_id=MGROUP_ID, post_id=post_id,
        offset=offset, count=comment_count
    )


@vk_request_errors
def get_user_photo(**kwargs):
    """
    :size:
    ( 'big'; medium'; 'small'; 'max' (smallest possible) )

    returns Photo
    # returns None if user have no avatar
    """
    photo_size = 'photo_' + kwargs['size']
    url = api.users.get(fields=photo_size)[0]

    # !always returns photo!
    if 'images/question_c.gif' not in url[photo_size]:
        return r.get(url[photo_size]).content


##########################
#                        #
#   ХРАНИМЫЕ ПРОЦЕДУРЫ   #
#                        #
##########################
#
#  GetIssuesCount
# var response = API.wall.get({"count":1, "filter":"others", "owner_id":Args.mgid});
# return response["count"];
#
#  GetMembersCount
# var response = API.groups.getById({"group_id": Args.gid, "fields":"members_count"});
# return response[0]["members_count"];
#
#  GetUserName
# var response = API.users.get()[0];
# return response["first_name"] + " " + response["last_name"];
#
