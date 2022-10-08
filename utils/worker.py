import os
import logging
from utils.functions import *
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime
from pytube import Search, YouTube


# noinspection PyUnresolvedReferences
class Worker(QObject):
    # Cria eventos
    print_on_terminal = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, artists: dict, count: int, path: str):
        super().__init__()

        self.artists = artists
        self.count = count
        self.path = path

        self.logger: logging.Logger | None = None
        self.err_count = 0

    def run(self):
        # Salva início da thread
        start_time = datetime.now()
        self.to_html(before='Preparando para começar...')

        if not os.path.exists(self.path):
            os.mkdir(self.path)

        # Realiza o loop
        self.download()

        # Calcula tempo de execução e média
        end_time = datetime.now()
        final = end_time - start_time

        duration = str(final).split('.')[0]
        media = str(final / self.count).split('.')[0]

        success = str(self.count - self.err_count + 1)

        # Informa o usuário
        self.to_html(before='-' * 48)
        self.to_html(highlight=(success, 'cyan'), after=' música(s) baixadas com sucesso.')

        if self.err_count:
            self.to_html(highlight=(str(self.err_count), 'red'), after=' música(s) com falha. Consulte o arquivo .log '
                         'salvo na pasta de destino para mais informações.')

        self.to_html(before='Tempo de execução: ', highlight=(duration, 'magenta'))
        self.to_html(before='Média de ', highlight=(media, 'green'), after=' por música.')

        # Emite sinal que a thread terminou
        self.finished.emit()

    def download(self):
        count = 0

        # Itera sobre o dicionário
        for artist, songs in self.artists.items():
            # Itera sobre cada música daquela chave do dicionário
            for song in songs:
                # Define nome para buscar no YouTube
                music_name = f'{artist} - {song}'

                # Tenta efetuar o download da música
                try:
                    # Caso seja uma url simplesmente tenta converter diretamente para um objeto de vídeo
                    if artist == 'urls':
                        stream = YouTube(song).streams.get_audio_only()
                        music_name = stream.title
                    else:
                        # Caso seja sem artista, usa o nome dado no aplicativo para buscar no YouTube
                        if artist == 'no_artist':
                            music_name = song

                        # Retorna a primeira ocorrência
                        stream = Search(music_name).results[0].streams.get_audio_only()

                        # Caso seja sem artista, define o nome do vídeo como nome do arquivo
                        if artist == 'no_artist':
                            music_name = stream.title

                    # Remove caracteres proibidos do título para salvar o arquivo
                    music_name = remove_forbidden_characters(music_name)

                    # Efetua o download e salva na pasta temporária com o nome definido acima
                    stream.download(output_path=self.path, filename=music_name + '.mp3')

                    self.to_html(highlight=(music_name, 'yellow'), after=' baixado com sucesso. '
                                                                         f'({count} / {self.count})')
                # Alerta usuário via terminal sobre possíveis erros
                except Exception as e:
                    self.to_html(before='Algo deu errado durante o download da música ', highlight=(music_name, 'red'))

                    err = e.message if hasattr(e, 'message') else e
                    error = f'Algo deu errado durante o download da música {music_name}\n'\
                            f'{e.__class__.__name__} {e.__context__}: {err}\n'

                    if not self.logger:
                        self.create_logger()

                    self.logger.error(error)
                    self.err_count += 1
                finally:
                    # Define progresso atual
                    count += 1
                    progress = int((count / self.count) * 100)

                    # Emite sinal para atualizar a barra de progresso
                    self.progress.emit(progress)

    def create_logger(self):
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d/%m/%y %H:%M:%S')

        handler = logging.FileHandler(os.path.join(self.path, '.log'), 'w')
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
