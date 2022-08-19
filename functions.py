import subprocess
import os
import zipfile
import chardet


def get_songs(file_name: str) -> tuple[dict, int]:
    artists = {}
    artist = None
    songs = []
    urls = []
    no_artists = []
    count = 0

    encoding = get_encoding(file_name)

    with open(file_name, 'r', encoding=encoding) as txt:
        for line in txt.readlines():
            line_content = line.strip()

            if 'https:' in line:
                urls.append(line_content)
                continue

            if line.startswith('*') or line.startswith('\n'):
                if artist and len(songs) > 0:
                    artists[artist] = songs.copy()

                songs.clear()
                artist = line_content[1:].title() if line.startswith('*') else None
                continue

            if not line.startswith('\n'):
                if artist:
                    songs.append(line_content.title())
                    count += 1
                else:
                    no_artists.append(line_content.title())

        if artist and len(songs) > 0:
            artists[artist] = songs.copy()

        if len(urls) > 0:
            artists['urls'] = urls.copy()
            count += len(urls)

        if len(no_artists) > 0:
            artists['no_artist'] = no_artists.copy()
            count += len(no_artists)

        return artists, count


def get_encoding(file_name):
    txt = open(file_name, 'rb').read()
    encoding = chardet.detect(txt)['encoding']

    return encoding


def convert_to_mp3(file_name: str):
    ffmpeg_path = '../../../ffmpeg/ffmpeg.exe'

    mp4_file_path = os.path.join('temp', file_name)
    mp3_file_path = mp4_file_path.replace('.mp4', '.mp3')

    subprocess.run(f'{ffmpeg_path} -loglevel warning -y -i "{mp4_file_path}" "{mp3_file_path}"')
    del_file(mp4_file_path)


def del_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def compact_to_zip(file_path):
    if not file_path:
        return

    zip_file = zipfile.ZipFile(file_path + '.zip', 'w')

    for root, dirs, files in os.walk('temp'):
        for file in files:
            fullpath = os.path.join(root, file)
            zip_file.write(fullpath, file, compress_type=zipfile.ZIP_DEFLATED)
            del_file(fullpath)

    zip_file.close()
    return True
