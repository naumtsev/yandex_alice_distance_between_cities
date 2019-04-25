from flask import Flask, request
import json
# импортируем функции из нашего второго файла geo
from geo import get_country, get_distance, get_coordinates, get_geo_info

app = Flask(__name__)

UsersINFO = dict()

@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = \
            'Привет! Я могу показать город или сказать расстояние между городами! Давай знакомиться! Меня зовут Алиса, а тебя как?'
        UsersINFO[user_id] =  dict()
        UsersINFO[user_id]['name'] = None
        return

    if UsersINFO[user_id]['name'] is None:
        name = get_name(req)
        if name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            UsersINFO[user_id]['name'] = name
            res['response']['text'] = 'Приятно познакомиться, {}. Назови один город, чтобы узнать страну, в которой он находится или два города, чтобы узнать расстояние между ними'.format(name)
        return
    else:
        cities = get_cities(req)
        if not cities:
            res['response']['text'] = '{}, ты не написал название не одного города!'.format(UsersINFO[user_id]['name'])

        elif len(cities) == 1:
            res['response']['text'] = 'Этот город в стране - ' + \
                                      get_geo_info(cities[0], 'country')
        elif len(cities) == 2:
            distance = get_distance( get_geo_info(cities[0], 'coordinates'),  get_geo_info(cities[1], 'coordinates'))
            res['response']['text'] = '{}, расстояние между этими городами: '.format(UsersINFO[user_id]['name']) + \
                                   str(round(distance)) + ' км.'
        else:
            res['response']['text'] = '{}, слишком много городов, я запуталась'.format(UsersINFO[user_id]['name'])


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value']:
                cities.append(entity['value']['city'])
    return cities

def get_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            if('first_name' in entity['value']):
                return entity['value']['first_name']
            return None


if __name__ == '__main__':
    app.run()