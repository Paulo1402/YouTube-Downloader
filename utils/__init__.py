import os
import socket
import re

from utils.worker import Worker
from utils.message import Message


__all__ = [
    'BASEDIR',
    'Worker',
    'Message',
    'remove_forbidden_characters',
    'check_connection',
    'get_old_data',
    'sort_dict',
    'count_media',
    'is_youtube_url',
    'is_youtube_playlist_url'
]

BASEDIR = os.path.dirname(os.path.dirname(__file__))


def get_old_data(data: dict, key: str, if_not_exists: list | dict) -> dict | list:
    """
    Retorna dados antigos ou um objeto novo.

    :param data: Dados
    :param key: Chave do dado
    :param if_not_exists: O que retornar caso não exista um dado anterior
    :return: Dado anterior ou objeto passado em "if_not_exists"
    """
    try:
        old_data = data[key]
    except KeyError:
        old_data = if_not_exists

    return old_data


def count_media(data: dict) -> int:
    """
     Retorna quantidade de mídias.

    :param data: Dados da tree
    :return: Quantidade de mídias
    """
    count = 0

    for key, extensions in data.items():
        for extension, songs in extensions.items():
            for _ in songs:
                count += 1

    return count


def is_youtube_url(url: str) -> bool:
    """
    Verifica se é uma URL do YouTube.

    :param url: URL como string
    :return: True se for YouTube, do contrário False
    """
    match = re.match(r'(^http(s)?://(www.)?(youtube\.com/(watch\?v=|playlist\?list=)|youtu\.be/)\S+$)', url)
    return bool(match)


def is_youtube_playlist_url(url: str):
    """
    Verifica se é uma URL do YouTube.

    :param url: URL como string
    :return: True se for playlist do YouTube, do contrário False
    """
    match = re.match(r'(^http(s)?://(www.)?youtube\.com/playlist\?list=\S+$)', url)
    return bool(match)


def sort_dict(data: tuple) -> str:
    """
    Organiza dados por ordem alfabética.
    Força com que "no_artist" e "urls" sejam as últimas chaves.

    :param data: Tupla com dados
    :return: Caractere para definir ordem
    """

    if data[0] == 'no_artist':
        return 'z' * 100
    elif data[0] == 'urls':
        return 'z' * 200
    else:
        return data[0]


def remove_forbidden_characters(file_name: str) -> str:
    """
    Remove caracteres proibidos no Windows.

    :param file_name: Nome do arquivo
    :return: Nome do arquivo sem caracteres proibidos
    """
    forbidden_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    new_file_name = ''

    for i in file_name:
        if i not in forbidden_characters:
            new_file_name += i

    return new_file_name if new_file_name else file_name


def check_connection() -> bool:
    """
    Checa se o usuário está conectado a internet.

    :return: True se houver conexão, do contrário False
    """
    try:
        socket.create_connection(('www.google.com', 80))
        return True
    except OSError:
        return False
