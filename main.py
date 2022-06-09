#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
import datetime
import requests
import json

ids = []

Headers = {
    'Accept': 	'application/json',
    'X-Auth-Token': '',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'tinder-version': '3.25.0',
}


def GoLikes():
    global mysql , ms
    users_id = []

    likes_count = 1

    while True:
        # если лайков не нашлось, то отдыхаем 20 минут
        if (likes_count == 0):
            SendMessageForMatches()
            print("Лайков нет, жду 10 минут, авось появятся")
            time.sleep(10 * 60)
        try:
          time.sleep(2)
          response = requests.get('https://api.gotinder.com/v2/recs/core?locale=ru' , headers = Headers)
        except:
            print("Хуйня с запросом")

        likes_count = 0

        try:
            data = json.loads(response.content)
        except:
            if (response.status_code == 401):
                print("Ошибка доступа, требуется обновить ключ авторизации")
                return 0
        #  print(data)
        if (data['meta']['status'] == 429):
          print("Tinder пидор не хочет отдавать данные")
          print(data)
          time.sleep(60)
          continue

        if (data['meta']['status'] == 200):
            for d in data['data']['results']:
                user = []
                birth_date = None
                skeep_like = 0
                if (not '_id' in d['user']):
                    continue
                print("d['user']['_id']" , d['user']['_id'])
                user.append(d['user']['_id'])
                user_id = d['user']['_id']

                print("d['user']['name']" , d['user']['name'])
                user.append(d['user']['name'])

                print("d['user']['bio']" , d['user']['bio'])
                user.append(d['user']['bio'])

                if(not 'birth_date' in d['user']):
                    birth_date = None
                else:
                    s = d['user']['birth_date']
                    birth_date = datetime.datetime(year=int(s[0:4]), month=int(s[5:7]), day=int(s[8:10]) , hour=int(s[11:13]) , minute=int(s[14:16]))
                print("d['user']['birth_date']" , birth_date)
                user.append(birth_date)

                if (not 'city' in d['user']):
                    print('None')
                    user.append(None)
                else:
                    print("d['user']['city']['name']" , d['user']['city']['name'])
                    user.append(d['user']['city']['name'])

                user.append(birth_date)

                if (d["user"]["bio"] == ''):
                    skeep_like = 1
                    print("Нет описания, нахуй таких")

                print('')

                if (skeep_like == 1):
                    continue

                url = 'https://api.gotinder.com/like/%s?locale=ru' % user_id
                response = requests.post(url , headers = Headers , data = {'s_number' : d["s_number"]} )
                like_data = json.loads(response.content)
                if (like_data['match'] != False):
                    #  SendMessageForMatches()
                    pass
                #      os.exit(0)

                if (like_data['likes_remaining'] != 0):
                    print("like user_id" , user_id)

                if (like_data['likes_remaining'] == 0):
                    print("Больше лайков нет!")
                    print(like_data['rate_limited_until'])
                    # добавляю 4 часа до Самарского времени
                    date = int(str(like_data['rate_limited_until'])[0:10]) + 4 * 60 * 60
                    date_int = date
                    wait_time = date - (int(time.time()) + 4 * 60 * 60)
                    date = datetime.datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
                    print("Требуется подождать до", date)
                    while ( date_int > (int(time.time()) + 4 * 60 * 60)):
                        print("Осталось ждать", wait_time / 60 , "минут")
                        SendMessageForMatches()
                        time.sleep(60 * 5)
                        wait_time = date_int - (int(time.time()) + 4 * 60 * 60)

                    GoLikes()
                    return 0
                time.sleep(2)
                likes_count += 1
        else:
            print("Что-то пошло не так с запросом")
            print(data)
            return 1

def SendLike(user_id , s_number):
    url = 'https://api.gotinder.com/like/%s?locale=ru' % user_id
    response = requests.post(url , headers = Headers , data = {'s_number' : s_number} )
    print (response.content)

# список сообщений
def GetMessages():
    url = 'https://api.gotinder.com/v2/matches?locale=ru&count=60&message=1&is_tinder_u=false'
    response = requests.get( url , headers = Headers)

    print(response.content)
    data = json.loads(response.content)
    #  print(data['data']['matches'][0]['messages'])
    #  print(data['data']['matches'][1]['messages'])
    for i in data['data']['matches']:
        if ('last_seen_msg_id' in i['seen']):
            print(i['seen']['last_seen_msg_id'])
        else:
            print(i['seen'])
        print(i['_id'])
        print(i['id'])
        print(i['created_date'])
        print('last_activity_date' , i['last_activity_date'])
        print(i['messages'][0]['to'])
        print(i['messages'][0]['message'])
        #  ids.append(i['messages'][0]['to'])
        print(i['pending'])
        print(i['person']['_id'])
        print(i['person']['ping_time'])
        print(i['person']['name'])
        print('')

# список полученных взаимных симпатий
def GetMatches():
    url = 'https://api.gotinder.com/v2/matches?locale=ru&count=60&message=0&is_tinder_u=false'
    response = requests.get( url , headers = Headers)
    print(response.content)
    data = json.loads(response.content)
    for d in data['data']['matches']:
        print(d)

# отправляю сообщения пользователям с кем произошло совпадение
def SendMessageForMatches():
    url = 'https://api.gotinder.com/v2/matches?locale=ru&count=60&message=0&is_tinder_u=false'
    response = requests.get( url , headers = Headers)
    #  print(response.content)
    data = json.loads(response.content)
    for d in data['data']['matches']:
        print(d['_id'])
        url = 'https://api.gotinder.com/user/matches/%s' % d['_id']
        response = requests.post(url , headers = Headers , data = {'message' : 'Тут надо написать сообщение которое ты хочешь отправить первым'} )
        print (response.content)


SendMessageForMatches()
GoLikes()
