from main import *
from form import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QApplication
from datetime import timedelta
import sys


def exception_hook(exctype, value, traceback):
    sys.__excepthook__(exctype, value, traceback)
    sys.exit(1)


class App(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.download_thread: QThread | None = None

        self.btDownload.clicked.connect(self.download_songs)
        self.btImportTxt.clicked.connect(self.import_txt)

    def closeEvent(self, event):
        if self.download_thread:
            if self.download_thread.isRunning():
                if messagebox.askquestion('ATENÇÃO', 'Processo em andamento!\n'
                                                     'Deseja sair mesmo assim?') == 'no':
                    event.ignore()
                    return

        event.accept()

    def import_txt(self):
        path = QFileDialog.getOpenFileName(self.centralwidget, 'Importar .txt', '.', 'txt (*.txt)')[0]

        if path:
            encoding = get_encoding(path)

            with open(path, 'r', encoding=encoding) as txt:
                self.txtSongs.clear()
                self.txtSongs.setText(txt.read())

    def download_songs(self):
        if self.download_thread:
            if self.download_thread.isRunning():
                messagebox.showerror('Já existe um processo em andamento. Por favor aguarde.')
                return

        song_list = self.txtSongs.toPlainText()

        with open('music_list.txt', 'w') as txt:
            txt.write(song_list)

        artists, count = get_songs('music_list.txt')

        if not count:
            messagebox.showerror('ATENÇÃO', 'Nenhuma música encontrada, verifique por favor. Na dúvida clique no '
                                            'botão help.')
            return

        estimate = str(timedelta(seconds=count * 3))
        if messagebox.askquestion('ATENÇÃO', 'Deseja fazer o download? \n'
                                             f'Tempo estimado: {estimate}') == 'no':
            return

        self.txtTerminal.clear()

        self.download_thread = DownloadThread(self.centralwidget, self.progressBar, self.txtTerminal, artists, count)
        self.download_thread.start()


if __name__ == "__main__":
    sys.excepthook = exception_hook
    qt = QApplication(sys.argv)
    app = App()
    app.show()

    sys.exit(qt.exec())
