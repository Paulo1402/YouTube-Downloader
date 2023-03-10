import os
import logging
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal
from pytube import Search, YouTube, Playlist

import utils


class Worker(QObject):
    # Cria eventos
    print_on_terminal = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, data: dict, path: str):
        super().__init__()

        self.data = data
        self.root = path
        self.count = utils.count_media(data)

        self.logger: logging.Logger | None = None

    def run(self):
        # Salva início da thread
        start_time = datetime.now()
        self.to_html(before='Preparando para começar...')

        if not os.path.exists(self.root):
            os.mkdir(self.root)

        # Realiza o loop
        err_count = self.download_medias()

        # Calcula tempo de execução e média
        end_time = datetime.now()
        final = end_time - start_time

        duration = str(final).split('.')[0]
        media = str(final / self.count).split('.')[0]

        success = str(self.count - err_count)

        # Informa o usuário
        self.to_html(highlight=(success, 'cyan'), after=' mídia(s) baixada(s) com sucesso.')

        if err_count:
            self.to_html(highlight=(str(err_count), 'red'), after=' mídia(s) com falha. Consulte o arquivo .log '
                         'salvo na pasta de destino para mais informações.')

        self.to_html(before='Tempo de execução: ', highlight=(duration, 'magenta'))
        self.to_html(before='Média de ', highlight=(media, 'green'), after=' por mídia.')

        # Emite sinal que a thread terminou
        self.finished.emit()

    def download_medias(self):
        def download(key: str, media: str, extension: str, path: str):
            nonlocal count, err_count

            media_name = f'{key} - {media}'

            # Tenta efetuar o download
            try:
                # Caso seja uma url tenta converter diretamente para um objeto de vídeo
                if key == 'urls':
                    # Se for uma playlist chama a função recursivamente para cada item da playlist
                    if utils.is_youtube_playlist_url(media):
                        playlist = Playlist(media)

                        for i, url in enumerate(playlist.video_urls, start=1):
                            if i < len(playlist):
                                self.count += 1

                            download(key, url, extension, path)

                        return

                    video = YouTube(media)
                    media_name = video.title
                else:
                    # Caso seja sem artista, procura pelo nome do vídeo
                    if key == 'no_artist':
                        media_name = media

                    # Retorna a primeira ocorrência
                    video: YouTube = Search(media_name).results[0]
                    media_name = video.title if key == 'no_artist' else media_name.title()

                if extension == 'mp3':
                    stream = video.streams.get_audio_only()
                else:
                    stream = video.streams.get_highest_resolution()

                # Remove caracteres proibidos do título para salvar o arquivo
                media_name = utils.remove_forbidden_characters(media_name)

                # Efetua o download e salva na pasta temporária com o nome definido acima
                stream.download(output_path=path, filename=f'{media_name}.{extension}')

                self.to_html(highlight=(media_name, 'yellow'), after=' baixado com sucesso. '
                                                                     f'({count + 1} / {self.count})')
            # Alerta usuário via terminal sobre possíveis erros
            except Exception as e:
                self.to_html(before='Algo deu errado durante o download da mídia ',
                             highlight=(media_name, 'red'))

                err = e.message if hasattr(e, 'message') else e
                error = f'Algo deu errado durante o download da mídia "{media_name}"\n' \
                        f'{e.__class__.__name__}-{e.__context__}: {err}\n'

                if not self.logger:
                    self.create_logger()

                self.logger.error(error)
                err_count += 1
            finally:
                # Define progresso atual
                count += 1
                progress = int((count / self.count) * 100)

                # Emite sinal para atualizar a barra de progresso
                self.progress.emit(progress)

        count = 0
        err_count = 0

        # Itera sobre o dicionário
        for key, extensions in self.data.items():
            if key == 'urls':
                key_parsed = 'URLS'
            elif key == 'no_artist':
                key_parsed = 'Sem Artista'
            else:
                key_parsed = key.title()

            path_key = os.path.join(self.root, key_parsed)

            # Cria pasta do artista
            if not os.path.exists(path_key):
                os.makedirs(path_key)

            for extension, medias in extensions.items():
                path_extension = os.path.join(path_key, extension.title())

                # Cria pasta da extensão
                if not os.path.exists(path_extension):
                    os.makedirs(path_extension)

                # Itera sobre cada música daquela chave do dicionário
                for media in medias:
                    download(key, media, extension, path_extension)

        return err_count

    # Cria arquivo de log
    def create_logger(self):
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d/%m/%y %H:%M:%S')

        handler = logging.FileHandler(os.path.join(self.root, '.log'), 'w')
        handler.setFormatter(formatter)
        handler.setLevel(logging.ERROR)

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(handler)

    # Monta a estrutura em HTML
    def to_html(self, before: str = '', highlight: tuple[str, str] = None, after: str = ''):
        html = f'<p style="line-height:1">{before}'

        if highlight:
            text = highlight[0]
            color = highlight[1]

            html += f'<span style="color:{color}">{text}</span>'

        html += f'{after}</p>'

        # Emite o sinal para printar no terminal e envia o HTML formatado como parâmetro
        self.print_on_terminal.emit(html)
