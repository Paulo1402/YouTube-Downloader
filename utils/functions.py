import subprocess
import os
import zipfile
import chardet


# Lê arquivo de texto temporário e define dicionário com base em um algoritmo
def get_songs(file_name: str) -> tuple[dict, int]:
    # Instancia variáveis
    artists = {}
    artist = None
    songs = []
    urls = []
    no_artists = []
    count = 0

    # Pega codificação
    encoding = get_encoding(file_name)

    # Abre arquivo para leitura
    with open(file_name, 'r', encoding=encoding) as txt:
        # Itera sobre as linhas
        for line in txt.readlines():
            # Remove quebra de linha
            line_content = line.strip()

            # Se houver 'https:' na linha adiciona na lista de urls
            if 'https:' in line:
                urls.append(line_content)
                continue

            # Se começar com '*' ou com uma quebra de linha
            if line.startswith('*') or line.startswith('\n'):
                # Se já houver um artista e a quantidade de músicas adicionadas for maior que 0, salva-o em um
                # dicionário
                if artist and len(songs) > 0:
                    artists[artist] = songs.copy()

                # Limpa a lista de músicas
                songs.clear()

                # Se a linha começar com '*' define novo artista, caso contrário define como None
                artist = line_content[1:].title() if line.startswith('*') else None
                continue

            # Caso começo da linha não seja uma quebra de linha
            if not line.startswith('\n'):
                # Se houver um artista definido adiciona na lista de músicas
                if artist:
                    songs.append(line_content.title())
                    count += 1
                # Do contrário, salva-a na lista de sem artistas
                else:
                    no_artists.append(line_content.title())

        # Se houver um artista pendente adiciona ao dicionário
        if artist and len(songs) > 0:
            artists[artist] = songs.copy()

        # Se houver urls adiciona ao dicionário
        if len(urls) > 0:
            artists['urls'] = urls.copy()
            count += len(urls)

        # Se houver sem artistas adiciona ao dicionário
        if len(no_artists) > 0:
            artists['no_artist'] = no_artists.copy()
            count += len(no_artists)

        # Retorna dicionário e quantidade de músicas
        return artists, count


# Retorna o tipo de codificação do arquivo .txt
def get_encoding(file_name):
    txt = open(file_name, 'rb').read()
    encoding = chardet.detect(txt)['encoding']

    return encoding


# Converte de .mp4 para .mp3 usando ffmpeg (Atualmente a conversão é feita na hora do download)
def convert_to_mp3(file_name: str):
    ffmpeg_path = '/ffmpeg/ffmpeg.exe'

    mp4_file_path = os.path.join('temp', file_name)
    mp3_file_path = mp4_file_path.replace('.mp4', '.mp3')

    subprocess.run(f'{ffmpeg_path} -loglevel warning -y -i "{mp4_file_path}" "{mp3_file_path}"')
    del_file(mp4_file_path)


# Remove um arquivo caso ele exista
def del_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


# Compacta conteúdo da pasta temporária em um arquivo .zip
def compact_to_zip(file_path):
    if file_path:
        zip_file = zipfile.ZipFile(file_path + '.zip', 'w')

        for root, dirs, files in os.walk('./temp'):
            for file in files:
                fullpath = os.path.join(root, file)
                zip_file.write(fullpath, file, compress_type=zipfile.ZIP_DEFLATED)

                del_file(fullpath)

        zip_file.close()
        return True


# Remove caracteres proibidos no Windows
def remove_forbidden_characters(file_name: str) -> str:
    forbidden_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    new_file_name = ''

    for i in file_name:
        if i not in forbidden_characters:
            new_file_name += i

    return new_file_name if new_file_name else file_name
