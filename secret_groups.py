import json

import requests
import time

VERSION = 5.68
TOKEN = str('TOKEN')


class MethodVK:
    """
    Обращение к методу вконтакте
    """
    def __init__(self, method, params):
        """
        :param method: имя метода API вконтакте
        :param options: словарь с параметрами реализуемого матода
        """
        self.method = method
        self.params = params

    def method_api(self):
        """
        Реализация метода API вконтакте
        :return: словарь с результатом
        """

        times = time.clock()

        response = requests.get(
            '/'.join(['https://api.vk.com/method', self.method]),
            self.params
        )

        time_process = time.clock() - times
        if time_process > 0.333333333333334:
            time.sleep(time_process - 0.333333333333334)

        return response.json()


class Friends:
    """
    Реализация метода Friends
    """
    def __init__(self, id):
        self.id = id

    def friends_get(self):
        """
        Возвращает словарь с параметрами матода Friends
        """
        params = {
            'user_id': self.id,
            'access_token': TOKEN,
            'version': VERSION
        }

        return params


class Groups:
    """
    Реализация метода Groupss
    """
    def __init__(self, id):
        self.id = id

    def groups_get(self):
        """
        Возвращает словарь с параметрами матода Groups
        """
        params = {
            'user_id': self.id,
            'extended': 0,
            'count': 1000,
            'access_token': TOKEN,
            'version': VERSION
        }

        return params

    def groups_get_full(self):
        """
        Возвращает словарь с расширенными параметрами матода Groups
        """
        params = {
            'user_id': self.id,
            'extended': 1,
            'fields': 'members_count',
            'count': 1000,
            'access_token': TOKEN,
            'version': VERSION
        }

        return params


def process_procent(whole, bit):
    """
    Возвращает часть от целого в процентах
    :param whole: целое
    :param bit: часть
    :return: выводит на экран полученый процент
    """

    rezult = (bit * 100) / whole

    if rezult != 100:
        return print('\rProcess: {}%'.format(int(rezult)), end='')
    elif rezult == 100:
        return print('\rProcess: Complited')


def groups_friends(list_id):
    """
    Возвращает множество gid групп всех друзей пользователя
    :param list_id: список id друзей пользователя
    :return: множество
    """
    set_rezult = set()
    bit = 1

    for id_friend in list_id:
        try:
            rezult = MethodVK('groups.get',
                              Groups(id_friend).groups_get()
                              ).method_api()['response']
        except KeyError:
            bit += 1
            continue

        rezult.pop(0)

        for gid in rezult:
            set_rezult.add(gid)

        process_procent(len(list_id), bit)
        bit += 1

    return set_rezult


def groups_json(list_groups_full, list_only_unit):
    """
    Возвращает словарь с группами в которые входит только пользователь
    :param list_groups_full: Расширенный список групп в которых состоит
    пользователь
    :param list_only_unit: Cписок груп пользователя в которые не входит ни
    один из друзей
    :return: Список словарей с ргуппами в которые входит только пользователь
    """
    groups = []

    for group in list_groups_full:
        rezult = {}
        if group['gid'] in list_only_unit:
            rezult['gid'] = group['gid']
            rezult['name'] = group['name']
            rezult['members_count'] = group['members_count']
        else:
            continue

        groups.append(rezult)

    return groups


def record_file(file_name, list_record):
    """
    Записывает данные в json фаил
    :param file_name: имя фаила
    :param list_record: записываемые данные
    """
    with open('.'.join([file_name, 'json']), 'w', encoding='utf-8') as file:
        json.dump(list_record, file, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    id = input('Введите id пользователя: ')

    # Получаем список id друзей пользователя
    list_id = MethodVK('friends.get',
                       Friends(id).friends_get()).method_api()['response']

    # Получаем список групп в которых состоит пользователь
    list_groups = MethodVK('groups.get',
                           Groups(id).groups_get()).method_api()['response']
    list_groups.pop(0)

    # Получаем множество групп в которые входят все друзья
    set_friends = groups_friends(list_id)

    # Получаем список груп пользователя в которые не входит ни один из друзей
    rezult_list = set(list_groups) - set_friends

    # Получаем расширенный список групп в которых состоит пользователь
    list_groups_full = MethodVK('groups.get',
                                Groups(id).groups_get_full()
                                ).method_api()['response']
    list_groups_full.pop(0)

    # Получаем список словарей с группами в которые входит только пользователь
    json_file = groups_json(list_groups_full, rezult_list)

    # Запиписываем результат в фаил
    record_file('groups', json_file)
