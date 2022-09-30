import shutil
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

    def __init__(self, artists: dict, count: int):
        super().__init__()

        self.artists = artists
        self.count = count

    def run(self):
        # Salva início da thread
        start_time = datetime.now()
        count = 0

        self.to_html(before='Preparando para começar...')

        # Prepara uma pasta temporária
        shutil.rmtree('./temp', ignore_errors=True)
        os.mkdir('./temp')

        # Itera sobre o dicionário para efetuar o download
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
                    stream.download(output_path='./temp', filename=music_name + '.mp3')

                    # Define progresso atual
                    count += 1
                    progress = int((count / self.count) * 100)

                    # Emite sinal para atualizar a barra de progresso
                    self.progress.emit(progress)

                    self.to_html(highlight=music_name, color='yellow', after=f' baixado com sucesso. '
                                 f'({count} / {self.count})')
                # Alerta usuário via terminal sobre possíveis erros
                except Exception as e:
                    err = e.message if hasattr(e, 'message') else e
                    print(f'{e.__class__.__name__} {e.__context__}: {err}')

                    self.to_html(before='Algo deu errado durante o download da música ',
                                 highlight=music_name, color='red')

        # Calcula tempo de execução e média
        end_time = datetime.now()
        final = end_time - start_time

        duration = str(final).split('.')[0]
        media = str(final / self.count).split('.')[0]

        # Informa o usuário
        self.to_html(before='-' * 40)
        self.to_html(before='Tarefa concluída. ', highlight=str(self.count), color='blue',
                     after=' música(s) baixadas com sucesso.')
        self.to_html(before='Tempo de execução: ', highlight=duration, color='magenta')
        self.to_html(before='Média de ', highlight=media, color='red', after=' por música.')

        # Emite sinal que a thread terminou
        self.finished.emit()

    # Monta a estrutura em HTML
    def to_html(self, before: str = '', after: str = '', highlight: str = '', color: str = 'red'):
        html = f'<p style="line-height:1">{before}'

        if highlight:
            html += f'<span style="color:{color}">{highlight}</span>'

        html += f'{after}</p>'

        # Emite o sinal para printar no terminal e envia o HTML formatado como parâmetro
        self.print_on_terminal.emit(html)
