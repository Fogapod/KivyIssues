# -*- coding: utf-8 -*-

import requests as r
import time
import re

from libs import vk

__author__ = 'Eugene Ershov - http://vk.com/fogapod'


api = None
token = None
kivy_ru = '99411738' # raw_id of http://vk.com/kivy_ru


def vk_request_errors(request):
    def request_errors(*args, **kwargs):
        # Для вывода ошибки в консоль
        # response = request(*args, **kwargs); time.sleep(0.66)
        try:
            response = request(*args, **kwargs)
        except Exception as error:
            error = str(error)
            if 'Too many requests per second' in error or 'timed out' in error:
                time.sleep(0.33)
                return request_errors(*args, **kwargs)

            elif 'Failed to establish a new connection' in error:
                print('Check your connection!')

            elif 'incorrect password' in error:
                print('Incorrect password!')

            elif 'Read timed out' in error or 'Connection aborted' in error:
                print('WARNING\nResponse time exceeded!')
                time.sleep(0.66)
                return request_errors(*args, **kwargs)

            elif 'Failed loading' in error:
                raise

            elif 'Captcha' in error:
                print('Capthca!!!!!')
                # raise #TODO обработать капчу

            elif 'Failed receiving session' in error:
                print('Error receiving session!')

            elif 'Auth check code is needed' in error:
                print('Auth code is needed!')

            else:
                if not api:
                    print('Authentication required')
                else:
                    print('\nERROR! ' + error + '\n')
            return False, error
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

    :return: string ( token )
    """
    set_group_id()

    scope = '204804'
    # 65536 -- offline; 8192 -- wall; 131072 -- docs; 4 -- photos
    app_id = '5720412'

    token = kwargs.get('token')
    key = kwargs.get('key')

    if token:
        session = vk.AuthSession(
            access_token=token, scope=scope, app_id=app_id
        )
    elif key:
        login, password = kwargs['login'], kwargs['password']
        session = vk.AuthSession(
            user_login=login, user_password=password,
            scope=scope, app_id=app_id, key=key
        )
    else:
        login, password = kwargs['login'], kwargs['password']
        session = vk.AuthSession(
            user_login=login, user_password=password,
            scope=scope, app_id=app_id
        )

    global api
    try:
        api = vk.API(session, v='5.60')
    except UnboundLocalError:
        raise Exception('Failed receiving session!')

    track_visitor()

    return session.access_token


@vk_request_errors
def get_members_count():
    """
    :return: string ( number )
    """
    return api.execute.GetMembersCount(gid=GROUP_ID)


@vk_request_errors
def get_user_name():
    """
    :return: string (First_name Last_name)
    """
    return api.execute.GetUserName()


@vk_request_errors
def get_issue_count():
    return api.execute.GetIssuesCount(mgid=MGROUP_ID)


@vk_request_errors
def get_issues(**kwargs):
    # TODO упорядочить получаемые данные через хранимые процедуры
    """
    :offset: ( :default: '0' )
    :count: ( :default: '30' )

    :return: dict
    """
    offset = kwargs.get('offset', '0')
    post_count = kwargs.get('count', '30')

    return api.wall.get(
        owner_id=MGROUP_ID, filter='others', extended='1',
        offset=offset, count=post_count
    )


@vk_request_errors
def create_issue(*args):
    """
    :issue_data: {'file','image','theme','issue'}

    :return: string ( post id )
    """
    issue_data = args[0]
    path_to_file = issue_data['file']
    path_to_image = issue_data['image']
    theme_text = issue_data['theme'] + '\n\n'
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
        + issue_text, attachments=attachments
    )


@vk_request_errors
def edit_issue(**kwargs):
    """
    """
    path_to_file = issue_data['file']
    doc_id = kwargs.get('doc_id')
    doc_oid = kwargs.get('doc_oid')

    path_to_image = issue_data['image']
    pic_id = kwargs.get('pic_id')
    pic_oid = kwargs.get('pic_oid')

    theme_text = issue_data['theme'] + '\n\n'
    issue_text = issue_data['issue']

    issue_id = kwargs['issue_id']

    attachments = []

    if path_to_file:
        doc = attach_doc(path=path_to_file)[0]
        attachments.append('doc' + str(doc[0]['owner_id'])
                         + '_' + str(doc[0['id']])
                        )

    elif doc_id and doc_oid:
        attachments.append('doc' + doc_oid + '_' + doc_id)


    if path_to_image:
        pic = attach_doc(path=path_to_image)[0]
        attachments.append('pic' + str(doc[0]['owner_id'])
                         + '_' + str(doc[0['id']])
                        )

    elif pic_id and pic_oid:
        attachments.append('pic' + pic_oid + '_' + pic_id)

    api.wall.edit(
        owner_id=MGROUP_ID, message=theme_text
        + issue_text, attachments=attachments, post_id=issue_id
        )


@vk_request_errors
def del_issue(**kwargs):
    """
    :issue_id:
    """
    pid = kwargs['issue_id']
    response = api.wall.delete(owner_id=MGROUP_ID, post_id=pid)
    if response:
        return True


@vk_request_errors
def attach_doc(**kwargs):
    """
    :path:

    :return: array with doc object
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
            response = api.docs.save(
                title=re.match('/.+$', path),
                file=json_data['file']
            )
            return response
        except Exception as e:
            raise Exception('Failed loading document ' + str(e))


@vk_request_errors
def attach_pic(**kwargs):
    """
    :path:

    :return: array with pic object
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
            response = api.photos.saveWallPhoto(
                group_id=GROUP_ID, photo=json_data['photo'],
                server=json_data['server'], hash=json_data['hash']
            )
            return response
        except Exception as e:
            raise Exception('Failed loading picture ' + str(e))


@vk_request_errors
def get_comments(**kwargs):
    # TODO упорядочить получаемые данные через хранимые процедуры
    """
    :post_id:
    :offset: ( :default: '0' )
    :count: ( :default: '100' )

    :return: dict with comments
    """
    post_id = kwargs['id']
    offset = kwargs.get('offset', '0')
    comment_count =kwargs.get('count', '100')

    return api.wall.getComments(
        owner_id=MGROUP_ID, post_id=post_id,
        offset=offset, count=comment_count,
        extended='1'
    )


@vk_request_errors
def create_comment(*args, **kwargs):
    """
    :comment_data: {'file', 'image', 'text'}
    :post_id:
    :reply_to:

    :return: comment_id
    """
    comment_data = args[0]
    path_to_file = comment_data['file']
    path_to_image = comment_data['image']
    text = comment_data['text']

    pid = kwargs['post_id']
    reply_to = kwargs.get('reply_to')

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

    return api.wall.createComment(
        owner_id=MGROUP_ID, message=text, 
        reply_to_comment=reply_to, post_id=pid,
        attachments=attachments
    )


@vk_request_errors
def edit_comment(**kwargs):
    """
    """
    path_to_file = issue_data['file']
    doc_id = kwargs.get('doc_id')
    doc_oid = kwargs.get('doc_oid')

    path_to_image = issue_data['image']
    pic_id = kwargs.get('pic_id')
    pic_oid = kwargs.get('pic_oid')

    text = kwargs['text']

    cid = kwargs['comment_id']

    attachments = []

    if path_to_file:
        doc = attach_doc(path=path_to_file)[0]
        attachments.append('doc' + str(doc[0]['owner_id'])
                         + '_' + str(doc[0['id']])
                        )

    elif doc_id and doc_oid:
        attachments.append('doc' + doc_oid + '_' + doc_id)


    if path_to_image:
        pic = attach_doc(path=path_to_image)[0]
        attachments.append('pic' + str(doc[0]['owner_id'])
                         + '_' + str(doc[0['id']])
                        )

    elif pic_id and pic_oid:
        attachments.append('pic' + pic_oid + '_' + pic_id)

    api.wall.editComment(
        owner_id=MGROUP_ID, message=text,
        attachments=attachments, comment_id=cid
        )


@vk_request_errors
def del_comment(**kwargs):
    """
    :comment_id:
    """
    cid = kwargs['comment_id']
    response = api.wall.deleteComment(owner_id=MGROUP_ID, comment_id=cid)
    if response:
        return True


@vk_request_errors
def get_user_photo(**kwargs):
    #FIXME всегда возвращает фото
    """
    :size:
    ( 'big'; medium'; 'small'; 'max' (smallest possible) )

    :return: Photo
    # :return: None if user have no avatar
    """
    photo_size = 'photo_' + kwargs['size']
    url = api.users.get(fields=photo_size)[0]

    if 'images/question_c.gif' not in url[photo_size]:
        return r.get(url[photo_size]).content


@vk_request_errors
def track_visitor():
    api.stats.trackVisitor()


def set_group_id(new_gid=kivy_ru):
    global GROUP_ID, MGROUP_ID
    GROUP_ID = str(new_gid)
    MGROUP_ID = '-' + GROUP_ID


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
