import os
import socket
import re

from utils.worker import Worker
from utils.message import Message


__all__ = [
    'remove_forbidden_characters',
    'check_connection',
    'get_old_data',
    'sort_dict',
    'count_media',
    'is_youtube_url',
    'is_youtube_playlist_url',
    'BASEDIR',
    'Worker',
    'Message'
]

BASEDIR = os.path.dirname(os.path.dirname(__file__))


def get_old_data(data: dict, key: str, if_not_exists: list | dict):
    try:
        old_data = data[key]
    except KeyError:
        old_data = if_not_exists

    return old_data


def count_media(data: dict):
    count = 0

    for key, extensions in data.items():
        for extension, songs in extensions.items():
            for _ in songs:
                count += 1

    return count


def is_youtube_url(url: str):
    match = re.match(r"http(s)?://(www.)?youtube\.com/watch\?v=|youtu\.be/", url)
    return bool(match)


def is_youtube_playlist_url(url: str):
    match = re.match(r'http(s)?://(www.)?youtube\.com/playlist\?list=', url)
    return bool(match)


def sort_dict(data: tuple):
    if data[0] == 'no_artist':
        return 'z' * 100
    elif data[0] == 'urls':
        return 'z' * 200
    else:
        return data[0]


# Remove caracteres proibidos no Windows
def remove_forbidden_characters(file_name: str) -> str:
    forbidden_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    new_file_name = ''

    for i in file_name:
        if i not in forbidden_characters:
            new_file_name += i

    return new_file_name if new_file_name else file_name


# Checa se o usuário está conectado a internet
def check_connection():
    try:
        socket.create_connection(('www.google.com', 80))
        return True
    except OSError:
        pass

# https://youtube.com/playlist?list=PLdv7EOMbqaGeSB14ixFfO-ksE2hj120A-