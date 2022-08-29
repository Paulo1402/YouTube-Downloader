from functions import *
from PyQt5.QtWidgets import QWidget, QProgressBar, QTextEdit, QFileDialog
from PyQt5.QtCore import QThread
from PyQt5 import QtGui
from tkinter import messagebox
from datetime import datetime
from pytube import Search, YouTube


class DownloadThread(QThread):
    def __init__(self, centralwidget: QWidget, progress_bar: QProgressBar, terminal: QTextEdit, artists: dict,
                 count: int):
        super().__init__()
        self.centralwidget = centralwidget
        self.progress_bar = progress_bar
        self.terminal = terminal
        self.artists = artists
        self.count = count

    def __del__(self):
        self.wait()

    def run(self):
        start_time = datetime.now()
        count = 0

        self.print_on_terminal(before='Preparando para começar...')

        if not os.path.exists('temp'):
            os.mkdir('temp')

        for file in os.scandir('temp'):
            os.remove(file.path)

        for artist, songs in self.artists.items():
            for song in songs:
                music_name = f'{artist} - {song}'

                try:
                    if not artist == 'urls':
                        if artist == 'no_artist':
                            music_name = song

                        stream = Search(music_name).results[0].streams.get_audio_only()

                        if artist == 'no_artist':
                            music_name = stream.title
                    else:
                        stream = YouTube(song).streams.get_audio_only()
                        music_name = stream.title

                    music_name = remove_forbidden_characters(music_name)
                    stream.download(output_path='temp', filename=music_name + '.mp3')

                    count += 1
                    progress = int((count / self.count) * 100)
                    self.progress_bar.setValue(progress)

                    self.print_on_terminal(highlight=music_name, color='yellow', after=f' baixado com sucesso. '
                                                                                       f'({count} / {self.count})')
                except Exception as e:
                    err = e.message if hasattr(e, 'message') else e
                    print(f'{e.__class__.__name__} {e.__context__}: {err}')

                    self.print_on_terminal(before='Algo deu errado durante o download da música ',
                                           highlight=music_name, color='red')

        end_time = datetime.now()
        final = end_time - start_time

        duration = str(final).split('.')[0]
        media = str(final / self.count).split('.')[0]

        self.print_on_terminal(before='-' * 80)
        self.print_on_terminal(before='Tarefa concluída. ', highlight=str(self.count), color='blue', after=' música(s) '
                                                                                                           'baixadas '
                                                                                                           'com '
                                                                                                           'sucesso.')
        self.print_on_terminal(before='Tempo de execução: ', highlight=duration, color='magenta')
        self.print_on_terminal(before='Média de ', highlight=media, color='red', after=' por música.')

        messagebox.showinfo('AVISO', 'Download Concluído.')

        path = QFileDialog.getSaveFileName(self.centralwidget, 'Salvar em', 'Músicas_Baixadas')[0]

        if compact_to_zip(path):
            messagebox.showinfo('AVISO', 'Músicas compactadas com sucesso..')

    def print_on_terminal(self, before: str = '', after: str = '', highlight: str = '', color: str = 'red'):
        if not before and not after and not highlight:
            return

        html = f'<p style="line-height:1">{before}'

        if highlight:
            html += f'<span style="color:{color}">{highlight}</span>'

        html += f'{after}</p>'
        self.terminal.append(html)

        cursor = self.terminal.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.terminal.setTextCursor(cursor)
