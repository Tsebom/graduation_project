import json

import requests
import time

VERSION = 5.68
TOKEN = str('b7a01500f18d4f40dff3df150a68648a7296dff5318ee0196c5c76d50d5e41cea'
            '96e2952c7e49121190bd')


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
        if time_process < 0.333333333333334:
            time.sleep(0.333333333333334 - time_process)

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
    Реализация метода Groups
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
        return print('\rProcessing: {}%'.format(int(rezult)), end='')
    elif rezult == 100:
        return print('\rProcessing: Complited')


def groups_user(list_gid):
    """
    Возвращает словарь, где key=gid группы пользователя, а value=0
    :param list_gid: список gid идентификаторов групп пользователя
    :return: словарь групп пользователя
    """
    groups = {}

    for value in list_gid:
        groups[value] = 0

    return groups


def groups_friends(groups_dict, list_id):
    """
    Словарь групп с количеством друзей входящих в каждую группу
    :param groups_dict: словарь, где key=gid группы пользователя, а value=0
    :param list_id: список id друзей пользователя
    :return: словарь, где key=gid группы пользователя, а value=кол-во друзей
    пользователя входящих в ту же группу
    """

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
            if groups_dict.get(gid) is None:
                continue
            else:
                groups_dict[gid] += 1

        process_procent(len(list_id), bit)
        bit += 1

    return groups_dict


def choose_groups(groups, friends):
    """
    Список групп с искомым вхождением кол-ва друзей
    :param groups: словарь групп с кол-ом входящих в них друзей
    :param friends: кол-во друзей
    :return: искомый список
    """
    list_gid = []

    for item, value in groups.items():
        if value <= friends:
            list_gid.append(item)

    return list_gid


def groups_json(list_groups_full, list_groups):
    """
    Список словарей с расширенными данными групп
    :param list_groups_full: расширенный список групп в которых состоит
    пользователь
    :param list_groups: искомый список групп
    :return: список словарей с расширенными данными групп
    """
    groups = []

    for group in list_groups_full:
        rezult = {}
        if group['gid'] in list_groups:
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
    quantity = input(
        'Введите максимальное количество друзей входящи в группу: ')

    # Получаем список id друзей пользователя
    list_id = MethodVK('friends.get',
                       Friends(id).friends_get()).method_api()['response']

    # Получаем список групп в которых состоит пользователь
    list_groups = MethodVK('groups.get',
                           Groups(id).groups_get()).method_api()['response']
    list_groups.pop(0)

    # Получаем словарь с группами и кол-ом друзей состоящих в этих группах
    groups = groups_friends(groups_user(list_groups), list_id)

    # Получаем список искомых групп
    rezult_list = choose_groups(groups, int(quantity))

    # Получаем расширенный список групп в которых состоит пользователь
    list_groups_full = MethodVK('groups.get',
                                Groups(id).groups_get_full()
                                ).method_api()['response']
    list_groups_full.pop(0)

    # Получаем искомый список словарей групп с расширенными данными
    json_file = groups_json(list_groups_full, rezult_list)

    # Запиписываем результат в фаил
    record_file('groups', json_file)
