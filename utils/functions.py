import chardet
import socket


# Lê arquivo de texto temporário e define dicionário com base em um algoritmo
def get_songs(song_list: str) -> tuple[dict, int]:
    # Instancia variáveis
    artists = {}
    songs = []
    urls = []
    no_artists = []

    artist = None
    count = 0

    # Itera sobre as linhas
    for line in song_list.splitlines():
        # Remove espaços em branco em excesso
        line_content = line.strip()

        # Se houver 'https:' na linha adiciona na lista de urls
        if 'https:' in line_content:
            urls.append(line_content)
        # Se a linha começa com '*' ou é vazia (em branco)
        elif line_content.startswith('*') or not line_content:
            # Se já houver um artista e a quantidade de músicas adicionadas for maior que 0, salva-o em um dicionário
            if artist and len(songs) > 0:
                artists[artist] = songs.copy()

            # Limpa a lista de músicas
            songs.clear()

            # Se a linha começar com '*' define novo artista, caso contrário define como None
            if line.startswith('*'):
                artist = line_content[1:].title()
            else:
                artist = None
            # Caso contrário é uma música
        else:
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
        return False
