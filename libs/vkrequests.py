# -*- coding: utf-8 -*-

import requests as r
import time
import re

from libs import vk

__author__ = 'Eugene Ershov - http://vk.com/fogapod'

api = None
token = None
kivy_ru = '99411738'  # raw_id of http://vk.com/kivy_ru


# vk.logger.setLevel('DEBUG')

def vk_request_errors(request):
    def request_errors(*args, **kwargs):
        # response = request(*args, **kwargs); time.sleep(0.66)
        # Для вывода ошибки в консоль
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
            # TODO обработать капчу

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
    """
    :token: ключ доступа для работы с аккаунтом ( str )
    :key: код подтверждения при двухфакторной авторизации ( int )
    :login: логин ( str )
    :password: пароль ( str )

    Возвращает: новое значение token ( str )

    """

    set_group_id()

    # 65536 == offline; 4096 == messages; 8192 == wall; 131072 == docs;
    # 4 == photos;
    scope = '208900'
    app_id = '5720412'

    token = kwargs.get('token')
    key = kwargs.get('key')

    if token:
        session = vk.AuthSession(access_token=token, scope=scope,
                                 app_id=app_id)
    elif key:
        login, password = kwargs['login'], kwargs['password']
        session = vk.AuthSession(user_login=login, user_password=password,
                                 scope=scope, app_id=app_id, key=key)
    else:
        login, password = kwargs['login'], kwargs['password']
        session = vk.AuthSession(user_login=login, user_password=password,
                                 scope=scope, app_id=app_id)

    global api
    try:
        api = vk.API(session, v='5.60')
    except UnboundLocalError:
        raise Exception('Failed receiving session!')

    track_visitor()

    return session.access_token


@vk_request_errors
def get_members_count():
    """Возвращает: число участников"""

    return api.execute.GetMembersCount(gid=GROUP_ID)


@vk_request_errors
def get_user_name():
    """Возвращает: Имя_пробел_Фамилия"""

    return api.execute.GetUserName()


@vk_request_errors
def get_issue_count():
    """Возвращает: число записей в группе"""

    return api.execute.GetIssuesCount(mgid=MGROUP_ID)


@vk_request_errors
def get_group_info():
    """
    Возвращает: информацию о текущей группе ( dict )
    Структура словаря:
    {
        "id": id группы ( int ),
        "name": название группы,
        "screen_name": короткое имя группы,
        "is_closed": группа закрыта? ( bool ),
        "type": "group",
        "is_admin": пользователь является администратором? ( bool ),
        "is_member": пользователь состоит в группе? ( bool ),
        "description": текст описания группы,
        "members_count": число участников ( int ),
        "status": текст из статуса группы,
        "photo_50": ссылка на фото,
        "photo_100": ссылка на фото,
        "photo_200": ссылка на фото
    }

    """
    response = api.groups.getById(group_id=GROUP_ID,
                                  fields='description,members_count,status')
    return response[0]


@vk_request_errors
def get_user_info(**kwargs):
    """
    :user_id: id пользователя (если не указан, будет получена информация о себе)

    Возвращает: информацию о пользователе ( dict )
    Структура словаря:
    {
        "deactivated":
            возвращается только в том случае, если страница пользователя удалена, все следующие поля не будут возвращены
            возможные значения: 'deleted'; 'banned',

        "id": id пользователя ( int ),
        "first_name": имя,
        "last_name": фамилия,
        "nickname": отчество,
        "domain": короткая ссылка на страницу (если указана), иначе 'id' + "user_id",
        "screen_name": (идентично "domain"???),
        "sex": пол:
            0: не указан,
            1: женский,
            2: мужской,
        "bdate": дата рождения (DD.MM.YYYY или DD.MM), не возвращается, если скрыто,
        "maiden_name": девичья фамилия (возвращается только если указана),
        "country": страна (если указана):
            "id": id,
            "title": название,
        "city": город (если указан):
            "id": id,
            "title": название,
        "home_town" название родного города,
        "relatives": массив с данными родственников или []:
            "id": id страницы (может не возвращаться),
            "name": имя,
            "type": тип родственной связи:
                'child': сын/дочь,
                'sibling': брат/сестра,
                'parent': отец/мать,
                'grandparent': дедушка/бабушка,
                'grandchild': внук/внучка,
        "relation": семейное положение:
            1: не женат/не замужем,
            2: есть друг/подруга,
            3: помолвлен,
            4: женат/замужем,
            5: всё сложно,
            6: в активном поиске,
            7: влюблён/влюблена,
            8: в гражданском браке,
            0: не указано,
            "relation_partner": id партнёра (если указан в семейном положении),

        "counters": количество объектов на странице:
            "albums": альбомы,
            "videos": видео,
            "audios": аудиозаписи,
            "photos": фотографии,
            "notes": заметки,
            "friends": друзья,
            "groups": группы,
            "online_friends": друзья онлайн,
            "user_video": видео с пользователем,
            "followers": подписчики,
            "pages": объекты "интересные страницы",
        "followers_count": количество подписчиков,
        "common_count": количество общих друзей,
        "friend_status" статус дружбы с пользователем:
            0: друг,
            1: пользователю отправлена заявка,
            2: пользователь отправил заявку,
            3: не является другом,
        "lists": массив id списков друзей, в которых состоит пользователь,
        "last_seen": последний раз был в сети:
            "time": время в unixtime
            "platform": платформа
                1: мобильная версия,
                2: iphone,
                3: ipad,
                4: android,
                5: windows phone,
                6: приложения для windows,
                7: полная версия сайта,
                ???: возможно, есть и другие,

        "verified": страница подтверждена (есть галочка) ( bool ),
        "has_mobile": номер телефона пользователя известен? ( bool ),
        "has_photo": пользователь установил фотографию профиля? ( bool ),
        "is_friend": является ли пользователь другом? ( bool ),
        "is_hidden_from_feed" новости пользователя скрыты из ленты? ( bool ),
        "online": пользователь в сети ( bool ),
        "can_post": на стене пользователя можно оставлять посты? ( bool ),
        "can_see_all_posts": доступны ли записи других пользователей на стене? ( bool ),
        "wall_comments": доступны ли комментирование записей? ( bool )
        "can_see_audio": доступен ли список аудио? ( bool ),
        "can_send_friend_request": возможно ли отправить заявку на добавление в друзья или можно только подписаться ( bool ),
        "can_write_private_message": доступны ли личные сообщения? ( bool ),
        "blacklisted": пользователь заблокировал меня? ( bool ),
        "blacklisted_by_me": пользователь заблокирован мной? ( bool ),

        "timezone": временная зона ( int ),
        "activities": поле "деятельность" ( str ) или '',
        "interests": поле "интересы" ( str ) или '',
        "quotes": любимые цитаты ( str ) или '',
        "movies": поле "любимые фильмы" ( str ) или '',
        "about": поле "о себе" ( str ) или '',
        "books": поле "любимые книги" ( str ) или '',
        "games": поле "любимые игры" ( str ) или '',
        "music": поле "любимая музыка" ( str ) или '',
        "site": поле "сайт" ( str ) или '',
        "tv": поле "любимые телешоу" ( str ) или '',
        "status": статус пользователя ( str )
        "status_audio": информация о музыке в статусе (не возвращается, если в статус ничего не транслируется)
        "contacts": контакты, возвращается при наличии одного из пунктов:
            "mobile_phone": номер обильного телефона ( str ),
            "home_phone": номер домашнего телефона( str ),
        "exports": массив сервисов, в которые настроен экспорт записей или [],
        "personal" поле: "жизненная позиция". возвращается, если указано одно из полей:
            "political": политические предпочтения:
                1: коммунистические,
                2: социалистические,
                3: умеренные,
                4: либеральные,
                5: консервативные,
                6: монархические,
                7: ультраконсервативные,
                8: индифферентные,
                9: либертарианские,
            "langs": массив со строками (языки),
            "religion": религия ( str ),
            "inspired_by": источники вдохновения ( str ),
            "people_main": главное в людях:
                1: ум и креативность,
                2: доброта и честность,
                3: красота и здоровье,
                4: власть и богатство,
                5: смелость и упорство,
                6: юмор и жизнелюбие,
            "life main": главное в жизни:
                1: семья и дети,
                2: карьера и деньги,
                3: развлечения и отдых,
                4: наука и исследования,
                5: совершенствование мира,
                6: саморазвитие,
                7: красота и искусство,
                8: слава и влияние,
            "smoking": отношение к курению:
                1: резко негативное,
                2: негативное,
                3: компромиссное,
                4: нейтральное,
                5: положительное,
            "alcohol": отношение к алкоголю:
                1: резко негативное,
                2: негативное,
                3: компромиссное,
                4: нейтральное,
                5: положительное,
        
        "crop_photo": данные о точках, по которым вырезаны профильная и миниатюрная фотографии:
            "photo": объект фотографии, из которой было вырезано главное фото,
            "crop": координаты точек в процентах:
                "x": левая верхняя (x),
                "x2": правая нижняя (x),
                "y": левая верхняя (y),
                "y2": правая нижняя (y),
            "rect": квадратная фотография, вырезанная из "crop". имеет аналогичные поля,
        "photo_id": id фотографии ( str ) ('123456_123456') (может отсутствовать),
        "photo_50": ссылка на квадратное фото шириной в 50 пикселей,
        "photo_100": ссылка на квадратное фото шириной в 100 пикселей,
        "photo_200_orig": ссылка на оригинальное фото шириной в 200 пикселей,
        "photo_200": ссылка на квадратное фото шириной в 200 пикселей,
        "photo_400_orig": ссылка на оригинальное фото шириной в 400 пикселей,
        "photo_max": ссылка на квадратное фото максимальной ширины,
        "photo_max_orig": ссылка на оригинальное фото,

        "schools": массив объектов 'школа' со следующими полями:
            "id": id школы,
            "country": id страны расположения,
            "city": id города расположения,
            "name": название школы,
            "year_from": год начала обучения ( int ),
            "year_graduated": год выпуска ( int ),
            "class": буква класса,
            "speciality": специализация,
            "type": идентификатор типа (от 0 до 13)
            "type_str": строка, соответствующая идентификатору "type":
                0: 'школа',
                1: 'гимназий',
                3: 'лицей',
                4: 'школа-интернат',
                5: 'вечерняя школа',
                6: 'спортивная школа',
                7: 'художественная школа',
                8: 'колледж',
                9: 'профессиональный лицей',
                10: 'техникум',
                11: 'ПТУ',
                12: 'училище',
                13: 'школа искусств',
        "universities":
            "id": id университета,
            "country": id страны расположения,
            "city": id города расположения,
            "name": название университета,
            "faculty": id факультета,
            "faculty_name": название факультета,
            "chair": id кафедры,
            "chair_name": название кафедры,
            "graduation": год выпуска ( int ),
            "education_form": форма обучения,
            "education_status": статус ('выпускник'),
        "edication": высшее образование, возвращается при наличии одного из пунктов:
            "university": id университета,
            "university_name": название университета,
            "faculty": id факультета,
            "faculty_name": название факультета,
            "graduation": год окончания,
        "military": массив объектов "military" или []:
            "unit": номер части,
            "unit_id": id части,
            "country_id": id страны, в которой находится часть,
            "from": год начала службы,
            "until": год окончания службы,
        "career": место работы (если есть). опциональные значения:
            "group_id": id группы,
            "company": название места работы (если нет "group_id"),
            "country_id": id страны,
            "city_id": id города (если "city_name" недоступно),
            "city_name": название города (если "city_id" недоступно),
            "from": год начала работы,
            "until": год окончания работы,
            "position": должность,
        "occupation": занятие пользователя:
            "type": тип:
                'work',
                'school',
                'university',
            "id": id школы, вуза, группы,
            "name": название школы, вуза, работы,
    }
    """
    uid = kwargs.get('user_id')
    response = api.users.get(user_ids=uid, fields=\
        'photo_id,verified,sex,bdate,city,country,home_town,has_photo,photo_50,photo_100,photo_200_orig,photo_200,photo_400_orig,photo_max,photo_max_orig,online,lists,domain,has_mobile,contacts,site,education,universities,schools,status,last_seen,followers_count,common_count,occupation,nickname,relatives,relation,personal,connections,exports,wall_comments,activities,interests,music,movies,tv,books,games,about,quotes,can_post,can_see_all_posts,can_see_audio,can_write_private_message,can_send_friend_request,is_favorite,is_hidden_from_feed,timezone,screen_name,maiden_name,crop_photo,is_friend,friend_status,career,military,blacklisted,blacklisted_by_me'
                        )[0]
    return response


@vk_request_errors
def get_issues(**kwargs):
    """
    :offset:
        необходимое смещение при получении списка записей
        стандартное значение: 0
    :count:
        количество записей, которое необходимо получить за раз
        стандартное значение: 30
        максимальное значение: 200

    Возвращает: список записей группы ( dict )
    # TODO: описание структуры словаря

    """

    offset = kwargs.get('offset', '0')
    post_count = kwargs.get('count', '30')

    return api.wall.get(owner_id=MGROUP_ID, filter='others', extended='1',
                        offset=offset, count=post_count)


@vk_request_errors
def get_user_posts(**kwargs):
    """
    :user_id: id пользователя, записи которого необходимо получить
    :offset:
        необходимое смещение при получении списка записей
        стандартное значение: 0
    :count:
        количество записей, которое необходимо получить за раз
        стандартное значение: 30
        максимальное значение: 200

    Возвращает: список записей пользователя (идентично get_issues)

    """

    uid = kwargs['user_id']
    offset = kwargs.get('offset', '0')
    post_count = kwargs.get('count', '30')

    return api.wall.get(owner_id=uid, filter='others', extended='1',
                        offset=offset, count=post_count)


@vk_request_errors
def create_issue(*args):
    """
    agrs:
    :issue_data:
        {'file': путь к документу или None
        'image': путь к фотографии или None
        'issue': текст вопроса
        }

    Возвращает: id созданной записи ( int )

    """

    issue_data = args[0]
    path_to_file = issue_data['file']
    path_to_image = issue_data['image']
    issue_text = issue_data['issue']

    attachments = []

    doc = upload_doc(path=path_to_file)[0]
    pic = attach_pic_to_wall_post(path=path_to_image)[0]

    if doc:
        attachments.append(
            'doc' + str(doc[0]['owner_id']) + '_' + str(doc[0]['id']))
    if pic:
        attachments.append(
            'photo' + str(pic[0]['owner_id']) + '_' + str(pic[0]['id']))

    return api.wall.post(owner_id=MGROUP_ID, message=issue_text,
                         attachments=attachments)


# TODO: требует доработки.
@vk_request_errors
def edit_issue(**kwargs):
    path_to_file = issue_data['file']
    doc_id = kwargs.get('doc_id')
    doc_oid = kwargs.get('doc_oid')

    path_to_image = issue_data['image']
    pic_id = kwargs.get('pic_id')
    pic_oid = kwargs.get('pic_oid')

    issue_text = issue_data['issue']

    issue_id = kwargs['issue_id']

    attachments = []

    if path_to_file:
        doc = upload_doc(path=path_to_file)[0]
        attachments.append(
            'doc' + str(doc[0]['owner_id']) + '_' + str(doc[0['id']]))

    elif doc_id and doc_oid:
        attachments.append('doc' + doc_oid + '_' + doc_id)

    if path_to_image:
        pic = upload_doc(path=path_to_image)[0]
        attachments.append(
            'pic' + str(doc[0]['owner_id']) + '_' + str(doc[0['id']]))

    elif pic_id and pic_oid:
        attachments.append('pic' + pic_oid + '_' + pic_id)

    api.wall.edit(owner_id=MGROUP_ID, message=issue_text,
                  attachments=attachments, post_id=issue_id)


@vk_request_errors
def del_issue(**kwargs):
    """
    :issue_id: id записи, подлежащей удалению;

    """

    pid = kwargs['issue_id']
    response = api.wall.delete(owner_id=MGROUP_ID, post_id=pid)
    if response:
        return True


# Использование извне не предполагается.
@vk_request_errors
def upload_doc(**kwargs):
    """
    :path: путь к документу

    Возвращает:
    #TODO: описать, что же возвращает этот метод

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
            response = api.docs.save(title=re.match('/.+$', path),
                                     file=json_data['file'])
            return response
        except Exception as e:
            raise Exception('Failed loading document ' + str(e))


# Использование извне не предполагается.
@vk_request_errors
def attach_pic_to_wall_post(**kwargs):
    """
    :path: путь к фотографии;

    Возвращает:
    #TODO: описать, что же возвращает этот метод

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
            response = api.photos.saveWallPhoto(group_id=GROUP_ID,
                                                photo=json_data['photo'],
                                                server=json_data['server'],
                                                hash=json_data['hash'])
            return response
        except Exception as e:
            raise Exception('Failed loading picture ' + str(e))


# TODO упорядочить получаемые данные через хранимые процедуры
@vk_request_errors
def get_comments(**kwargs):
    """
    :post_id:
        id поста, комментарии под которым необходимо получить
    :offset:
        необходимое смещение при получении списка комментариев
        стандартное значение: 0
    :count:
        количество комментариев, которое необходимо получить за раз
        стандартное значение: 100
        максимальное значение: 200

    Возвращает: список комментариев ( dict )
    #TODO: описать структуру словаря

    """

    post_id = kwargs['id']
    offset = kwargs.get('offset', '0')
    comment_count = kwargs.get('count', '100')

    return api.wall.getComments(owner_id=MGROUP_ID, post_id=post_id,
                                offset=offset, count=comment_count,
                                extended='1')


@vk_request_errors
def create_comment(*args, **kwargs):
    """
    :comment_data:
        {'file': путь к документу или None,
         'image': путь к фотографии или None,
         'text': 'текст сообщения'};

    :post_id:
        id поста, под которым будет создан комментарий;

    :reply_to:
        новый комментарий будет отмечен как ответ на комментарий,
        id которого указан в данном параметре;

    Возвращает: id нового комментария;

    """

    comment_data = args[0]
    path_to_file = comment_data['file']
    path_to_image = comment_data['image']
    text = comment_data['text']

    pid = kwargs['post_id']
    reply_to = kwargs.get('reply_to')

    attachments = []

    doc = upload_doc(path=path_to_file)[0]
    pic = attach_pic_to_wall_post(path=path_to_image)[0]

    if doc:
        attachments.append(
            'doc' + str(doc[0]['owner_id']) + '_' + str(doc[0]['id']))
    if pic:
        attachments.append(
            'photo' + str(pic[0]['owner_id']) + '_' + str(pic[0]['id']))

    return api.wall.createComment(owner_id=MGROUP_ID, message=text,
                                  reply_to_comment=reply_to, post_id=pid,
                                  attachments=attachments)


# TODO: требует доработки.
@vk_request_errors
def edit_comment(**kwargs):
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
        doc = upload_doc(path=path_to_file)[0]
        attachments.append(
            'doc' + str(doc[0]['owner_id']) + '_' + str(doc[0['id']]))

    elif doc_id and doc_oid:
        attachments.append('doc' + doc_oid + '_' + doc_id)

    if path_to_image:
        pic = upload_doc(path=path_to_image)[0]
        attachments.append(
            'pic' + str(doc[0]['owner_id']) + '_' + str(doc[0['id']]))

    elif pic_id and pic_oid:
        attachments.append('pic' + pic_oid + '_' + pic_id)

    api.wall.editComment(owner_id=MGROUP_ID, message=text,
                         attachments=attachments, comment_id=cid)


@vk_request_errors
def del_comment(**kwargs):
    """
    :comment_id: id комментария, подлежащего удалению;

    """

    cid = kwargs['comment_id']
    response = api.wall.deleteComment(owner_id=MGROUP_ID, comment_id=cid)
    if response:
        return True


# FIXME всегда возвращает фото
@vk_request_errors
def get_user_photo(**kwargs):
    """
    :size: необходимый размер фотографии
        возможные значения (от большего к меньшему)
            'big'
            'medium'
            'small'
            'max'

    Возвращает: фото
    # Возвращает: None, если у пользователя нет аватара.

    """

    photo_size = 'photo_' + kwargs['size']
    url = api.users.get(fields=photo_size)[0]

    if 'images/question_c.gif' not in url[photo_size]:
        return r.get(url[photo_size]).content


@vk_request_errors
def get_messages_list(**kwargs):
    """
    :count:
        количество диалогов
        максимум: 200
        стандартное значение: 20

    :offset:
        смещение (offset 0 == последний активный диалог)
        стандартное значение: 0

    Возвращает: словарь со списком диалогов, для каждого диалога дано
                одно, последнее сообщение

    Структура ответа:
        {
            'count': общее число диалогов,
            'unread_dialogs': число диалогов с непрочитанными сообщениями
            'items':
                [
                    'unread':
                        количество непрочитанных сообщений в диалоге
                        (не возвращается при 'unread': 0),
                    'message':
                        {
                            'id':
                                id сообщения,

                            'date':
                                дата отправки в Unixtime,

                            'out':
                                исходящее (1/0),

                            'user_id':
                                id собеседника или того, кто отправил
                                последнее сообщение (беседа, группа),

                            'read_state':
                                прочитано (1/0),

                            'title':
                                ' ... ' для диалога; название беседы для
                                беседы; '' для сообщения от группы,

                            'body':
                                текст сообщения,

                            'from_id':
                                 id автора сообщения, # не приходит

                            'fwd_messages':
                                словарь переслынных сообщений (если есть),

                            'emoji':
                                есть ли в сообщении смайлики emoji (1/0)
                                # не всегда правильно

                            # дополнительные данные для беседы
                            'chat_id':
                                id беседы,

                            'chat_active':
                                идентификаторы авторов последних сообщений
                                беседы - массив с id, # ???

                            'push_settings':
                                настройки уведомлений (если есть)
                            {
                                'sound':
                                    включены уведомления со звуком (1/0),

                                'disabled_until':
                                    уведомления отключены до ( int )
                            },

                            'users_count':
                                число участников беседы,

                             'admin_id':
                                id создателя беседы,

                            'photo_50':
                                ссылка на фото,

                            'photo_100':
                                ссылка на фото,

                            'photo_200':
                                ссылка на фото,

                            'action':
                                тип действия (если это служебное сообщение):

                                'chat_photo_update' -
                                    обновлена фотография беседы;
                                'chat_photo_remove' -
                                    удалена фотография беседы;
                                'chat_create' -
                                    создана беседа;
                                'chat_title_update' -
                                    обновлено название беседы;
                                'chat_invite_user' -
                                    приглашен пользователь;
                                'chat_kick_user' -
                                    исключен пользователь;

                            'action_mid':
                                идентификатор пользователя (если > 0)
                                или email (если < 0), которого пригласили
                                или исключили (для служебных сообщений
                                с action = 'chat_invite_user'
                                или 'chat_kick_user')

                            'action_email':
                                email, который пригласили или исключили
                                (для служебных сообщений
                                с 'action' = 'chat_invite_user'
                                или 'chat_kick_user' и
                                отрицательным'action_mid')

                            'action_text':
                                название беседы (для служебных сообщений
                                с 'action' = 'chat_create'
                                или 'chat_title_update')
                            # дополнительные данные для беседы
                        }

                    'in_read':
                        id последнего прочитанного сообщения (пользователем),

                    'out_read':
                        id последнего прочитанного сообщения (собеседником)

                    'attachments':
                        словарь прикреплённых объектов (если есть)
                ]

        }

    """

    count = kwargs.get('count', 20)
    offset = kwargs.get('offset', 0)

    response = api.messages.getDialogs(
        count=count, offset=offset
        )
    return response


@vk_request_errors
def get_messages(**kwargs):
    """
    Загружает дополнительные сообщения из выбранного диалога
    :user_id: id собеседника
    :count:
        количество сообщений
        максимум: 200
        стандартное значение: 100
    :offset:
        смещение (offset 0 == последнее сообщение в диалоге)
        стандартное значение: 0
    Возвращает:
        Массив сообщений

    """

    uid = kwargs['user_id']
    count = kwargs.get('count', 100)
    offset = kwargs.get('offset', 0)

    response = api.messages.getHistory(
        count=count, offset=offset,
        user_id=uid
        )
    return response


@vk_request_errors
def send_message(**kwargs):
    """
    :user_id:
        id пользователя

    :group_id:
        id беседы

    :text:
        текст сообщения

    :messages_to_forward:
        строка с id сообщений, которые нужно переслать через запятую
        ('1,2,3') (опционально)

    :rnd_id:
        специальный идентификатор, необходимый для предотвращения отправки
        повторяющихся сообщений. Не нужно указывать,
        если в приложении не будет реализована функция автоответа

    :file:
        путь к документу (опционально)

    :image:
        путь к фотографии (опционально)

    :Возвращает: id нового сообщения

    """

    gid = None
    uid = kwargs.get('user_id')
    if not uid:
        gid = kwargs['group_id']
    text = kwargs['text']
    forward = kwargs.get('messages_to_forward')
    rnd_id = kwargs.get('rnd_id')

    path_to_file = kwargs.get('file')
    path_to_image = kwargs.get('image')

    attachments = []

    doc = upload_doc(path=path_to_file)[0]
    pic = attach_pic_to_message(path=path_to_image)[0]

    if doc:
        attachments.append(
            'doc' + str(doc[0]['owner_id']) + '_' + str(doc[0]['id']))
    if pic:
        attachments.append(
            'photo' + str(pic[0]['owner_id']) + '_' + str(pic[0]['id']))
    # print attachments
    response = api.messages.send(peer_id=uid,
        message=text, forward_messages=forward,
        chat_id=gid, random_id=rnd_id,
        attachment=attachments
    )

    return response


# Использование извне не предполагается.
@vk_request_errors
def attach_pic_to_message(**kwargs):
    """
    :path: путь к фотографии;

    Возвращает:
    #TODO: описать, что же возвращает этот метод

    """
    path = kwargs['path']

    if path:
        upload_data = api.photos.getMessagesUploadServer(group_id=GROUP_ID)

        pic = {'photo': open(path, 'rb')}

        response = r.post(upload_data['upload_url'], files=pic)
        json_data = response.json()

        if json_data['photo'] == '[]':
            raise Exception('Failed loading picture')

        try:
            response = api.photos.saveMessagesPhoto(group_id=GROUP_ID,
                                                photo=json_data['photo'],
                                                server=json_data['server'],
                                                hash=json_data['hash'])
            return response
        except Exception as e:
            raise Exception('Failed loading picture ' + str(e))


@vk_request_errors
def get_message_long_poll_data():
    """
    Возвращает: словарь ( dict )
    Структура ответа:
    {
        'key':str,
        'server':str,
        'ts':int
    }

    """

    response = api.messages.getLongPollServer()
    return response


@vk_request_errors
def do_message_long_poll_request(**kwargs):
    """
    :url: специальный url, собранный с использованием данных из get_message_long_poll_data()

    Этот метод должен быть запущен в отдельном потоке.
    Он вернёт ответ только когда случится определённое событие.
    
    Возвращает: json список событий или [] (если истекло время ожидания)

    Структура события:
        События различаются первой цифрой:
            1 - Замена флагов сообщения
                [1, id сообщения ( int ), сумма флагов]
                Возможные флаги сообщения:
                    1 - сообщение не прочитано
                    2 - исходящее сообщение
                    4 - на сообщение был создан ответ
                    8 - помеченное сообщение
                    16 - сообщение отправлено через чат
                    32 - сообщение отправлено другом
                    64 - сообщение помечено как "Спам"
                    128 - сообщение удалено (в корзине)
                    256 - сообщение проверено пользователем на спам
                    512 - сообщение содержит медиаконтент

            2 - Установка флагов сообщения
                [2, id сообщения ( int ), сумма флагов]

            3 - Сброс флагов сообщения
                [3, id сообщения ( int ), сумма флагов]

            4 - Обнаружено новое сообщение
                [
                    4,
                    id сообщения ( int ),
                    сумма флагов сообщения ( int ),
                    id назначения ( str )(для пользователя его id,
                    для беседы 2000000000 + id беседы, для группы -id группы
                    или id группы + 1000000000), время отправки сообщения в
                    Unixtime ( int ), тема сообщения (для диалога == ' ... ',
                    для беседы это название беседы), текст сообщения ( str ),
                    словарь вложений или {}, параметр random_id ( int ),
                    если он был передан при отправке сообщений
                    (нужен для предотвращения отправки одного сообщения
                    несколько раз)
                ]

            6 - Прочитаны входящие сообщения на данном отрезке
                [
                    6,
                    id назначения ( str )(для пользователя его id,
                    для беседы 2000000000 + id беседы, для группы -id группы
                    или id группы + 1000000000), до ( int )
                ]

            7 - Прочитаны исходящие сообщения на данном отрезке
                [
                    7,
                    id назначения ( str )(для пользователя его id;
                    для беседы 2000000000 + id беседы; для группы -id группы
                    или id группы + 1000000000), до ( int )
                ]

            8 - Друг зашёл на сайт
                [8, -id пользователя ( int ), extra???]

            9 - Друг вышел с сайта
                [9, -id пользователя ( int ), extra???]

            10 - Сброшен флаг диалога
                [10, флаг диалога]
                Флаги диалога:
                    1 - важный диалог
                    2 - диалог с ответом от группы

            11 - Заменён флаг диалога
                [11, флаг диалога]

            12 - Установлен флаг диалога
                [12, флаг диалога]

            51 - Изменились параметры беседы (название/состав)
                [51, id беседы ( int ),
                изменения сделаны пользователем (1/0)]

            61 - Пользователь начал набирать текст в диалоге
                [61, id пользователя ( int ), id диалога ( int )]

            62 - Пользователь начал набирать текст в беседе
                [62, id пользователя ( int ), id беседы ( int )]

            70 - Пользователь совершил звонок
                [70, id пользователя ( int ), идентификатор звонка ( int )]
                Идентификаторы звонка:
                    ???

            80 - Изменение счётчика непрочитанных сообщений
                [80, значение счётчика ( int ), 0]

            114 - Изменены настройки оповещений
                [
                    114,
                    id пользователя или беседы ( int ),
                    звуковые сообщения включены (1/0),
                    оповещения отключены до: -1 - навсегда; 0 - включены;
                    другое число - когда нужно включить
                ]

    Более полная информация о событиях:
    https://vk.com/dev/using_longpoll?f=3.%20%D0%A1%D1%82%D1%80%D1%83%D0%
    BA%D1%82%D1%83%D1%80%D0%B0%20%D1%81%D0%BE%D0%B1%D1%8B%D1%82%D0%B8%D0%B9

    """

    url = kwargs['url']
    return r.post(url)


@vk_request_errors
def track_visitor():
    """Отвечает за занесение в статистику приложения
    информации о пользователе."""

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
