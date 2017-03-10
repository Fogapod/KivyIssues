# -*- coding: utf-8 -*-

"""
Файл создан для демонстрации работы метода 
vkrequests.get_message_updates()
"""

import time

import vkrequests as vkr

token = '' # copy token here
authorized = False
while not authorized:
    if token:
        response, error = vkr.log_in(token=token)
    else:
        LOGIN = raw_input('login:')
        PASSWORD = raw_input('password:')
        response, error = vkr.log_in(login=LOGIN, password=PASSWORD)

    if response:
        authorized = True

    elif 'code is needed' in error:
        key = raw_input('key:')
        response, error = vkr.log_in(login=LOGIN, password=PASSWORD, key=key)
        if response:
            authorized = True

    print(u'\nУспешная авторизация\ntoken: ' + response)

class App():
    def __init__(self):
        self.mlpd = vkr.get_message_long_poll_data()[0]
        self.listen_message_updates = True

    def listen_for_updates(self):
        while self.listen_message_updates:
            response, error = vkr.get_message_updates(ts=self.mlpd['ts'],pts=self.mlpd['pts'])
            print(response)
 
            if response:
                updates = response[0]
                self.mlpd['pts'] = response[1]
                messages = response[2]
            else:
                break

            time.sleep(2) # проверять обновления каждые 2 секунды

if __name__ == '__main__':
    App().listen_for_updates()
