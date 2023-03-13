import sys
import os
import webbrowser
from typing import Callable

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QFileDialog, QMenu, QTreeWidget, QListWidget, QTreeWidgetItem, QListWidgetItem
)
from PyQt6.QtGui import QTextCursor, QIcon, QAction
from PyQt6.QtCore import QThread, Qt, QPoint

from ui.MainWindow import Ui_MainWindow
from utils import *


# Tela feita usando Qt Designer e convertida para Python com a biblioteca PyQt6 (pyuic6)

# Classe principal do aplicativo
class App(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Instancia variáveis
        self.thread: QThread | None = None
        self.worker: Worker | None = None
        self.path = ''
        self.data = {}

        # Inicia interface do aplicativo
        self.init_ui()

    def init_ui(self):
        # Seta propriedades iniciais
        self.cb_extension.setCurrentIndex(0)
        self.radio_name.setChecked(True)
        self.bt_download.setDisabled(True)
        self.tree_list.clear()
        self.txt_artist.setFocus()

        github_link = 'https://github.com/Paulo1402/YouTube-Downloader'

        # Conecta botões do menu
        self.action_project.triggered.connect(lambda: webbrowser.open(github_link))
        self.action_help.triggered.connect(lambda: webbrowser.open(f'{github_link}#-como-usar'))
        self.action_icons.triggered.connect(lambda: webbrowser.open('https://icons8.com.br/'))

        # Conecta eventos
        self.bt_download.clicked.connect(self.download)
        self.bt_add.clicked.connect(self.add_media)
        self.bt_append.clicked.connect(self.append_media)
        self.radio_name.toggled.connect(lambda x: self.txt_artist.setDisabled(not x))

        # Conecta atalhos de teclados ao botão para adicionar media
        enter_action = QAction(self)
        enter_action.setShortcuts(['return', 'enter'])
        enter_action.triggered.connect(self.handle_enter_pressed)
        self.addAction(enter_action)

        # Conecta atalhos do teclado para botões
        self.bt_download.setShortcut('CTRL+D')
        self.bt_add.setShortcut('CTRL+A')

        # Seta custom context menus
        self.tree_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_list.customContextMenuRequested.connect(
            lambda pos: self.custom_context(self.tree_list, self.remove_tree_item, pos)
        )

        self.list_media.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_media.customContextMenuRequested.connect(
            lambda pos: self.custom_context(self.list_media, self.remove_list_item, pos)
        )

    # Evento disparado ao tentar fechar o aplicativo
    def closeEvent(self, event):
        # Se a thread estiver em execução
        if self.thread and self.thread.isRunning():
            if Message.warning_question(self, 'Processo em andamento!\nDeseja sair mesmo assim?') == Message.NO:
                event.ignore()
                return

        self.finished_thread(force=True)
        event.accept()

    # Executa o botão de append caso os atalhos de teclado forem utilizados
    def handle_enter_pressed(self):
        if not self.txt_media.hasFocus():
            return

        self.bt_append.animateClick()

    # Remove item da list widget
    def remove_list_item(self, item: QListWidgetItem):
        row = self.list_media.row(item)
        self.list_media.takeItem(row)

    # Remove item do dicionário de dados e refaz a tree list
    def remove_tree_item(self, item: QTreeWidgetItem):
        parent = item.parent()

        # Artista
        if not parent:
            artist = item.text(0).lower()
            del self.data[artist]
        # Formato
        elif not parent.parent():
            artist = parent.text(0).lower()
            extension = item.text(0).lower()

            if artist == 'sem artista':
                artist = 'no_artist'

            artist_data = self.data[artist]
            del artist_data[extension]

            # Caso não haja outro formato, remove o artista
            if not artist_data:
                del self.data[artist]
        # Media
        else:
            artist = parent.parent().text(0).lower()
            extension = parent.text(0).lower()
            media = item.text(0)

            if artist == 'sem artista':
                artist = 'no_artist'
            elif artist != 'urls':
                media = media.lower()

            artist_data = self.data[artist]
            extension_data = artist_data[parent.text(0).lower()]

            index_media = extension_data.index(media)
            del extension_data[index_media]

            # Caso não haja outra media, remove o formato
            if not extension_data:
                del artist_data[extension]

                # Caso não haja outro formato, remove o artista
                if not artist_data:
                    del self.data[artist]

        # Recria tree list
        self.build_tree()

    # Cria um context menu com opção para deletar item
    def custom_context(self, main_widget: QTreeWidget | QListWidget, remove_function: Callable, pos: QPoint):
        if not main_widget.selectedItems():
            return

        item = main_widget.selectedItems()[0]
        pos = main_widget.mapToGlobal(pos)

        delete_action = QAction('Deletar', self)
        delete_action.setIcon(QIcon(os.path.join(BASEDIR, 'assets/delete-32.png')))
        delete_action.triggered.connect(lambda: remove_function(item))

        menu = QMenu(self)
        menu.addAction(delete_action)
        menu.move(pos)
        menu.show()

    # Adiciona media ao list widget
    def append_media(self):
        media: str = self.txt_media.text()

        if not media.strip():
            return

        self.list_media.addItem(media)

        self.txt_media.clear()
        self.txt_media.setFocus()

    # Adiciona media ao dicionário de dados
    def add_media(self):
        data = []
        artist: str = self.txt_artist.text()
        extension: str = self.cb_extension.currentText()
        search_by_url: bool = self.radio_url.isChecked()

        # Adiciona itens da list widget em uma lista temporária
        for i in range(self.list_media.count()):
            media = self.list_media.item(i).text()
            is_url = is_youtube_url(media) or is_youtube_playlist_url(media)

            # Verifica URL caso o modo de busca seja por URL
            if search_by_url and not is_url:
                Message.critical(
                    self,
                    'ATENÇÃO',
                    'Um ou mais itens na lista de vídeos não se parecem com uma URL válida!\n'
                    'Sua URL deve conter o seguinte padrão:\n'
                    '"https://www.youtube.com/watch?v=[ID DO VÍDEO]" '
                    'ou "https://www.youtube.com/playlist?list=[ID DA PLAYLIST]"'
                )
                return
            elif not search_by_url and is_url:
                Message.critical(
                    self,
                    'ATENÇÃO',
                    'Um ou mais itens na lista de vídeos são URLS, porém a opcão de busca por nome está selecionada!\n'
                    'Remova os demais itens e escolha a opção de busca por URL.'
                )
                return

            data.append(media)

        if len(data) == 0:
            Message.warning(self, 'ATENÇÃO', 'Insira ao menos um item na lista de vídeos para continuar!')
            self.txt_media.setFocus()
            return

        # Define key
        if search_by_url:
            key = 'urls'
        elif artist:
            key = artist
        else:
            key = 'no_artist'

        # Retorna dados
        media = get_old_data(self.data, key, {})

        # Verifica extensão
        if '.mp3' in extension:
            # Retorna dados antigos
            mp3_media = get_old_data(media, 'mp3', [])

            # Garante apenas registros únicos
            unique_data = [d for d in data if d not in mp3_media]

            # Salva medias na extensão escolhida
            media['mp3'] = [*mp3_media, *unique_data]

        # Repete o processo acima
        if '.mp4' in extension:
            mp4_media = get_old_data(media, 'mp4', [])
            unique_data = [d for d in data if d not in mp4_media]

            media['mp4'] = [*mp4_media, *unique_data]

        # Salva media no dicionário de dados
        self.data[key] = media

        # Prepara para novo registro
        self.txt_artist.clear()
        self.txt_media.clear()
        self.list_media.clear()
        self.radio_name.setChecked(True)
        self.cb_extension.setCurrentIndex(0)

        # Recria tree list
        self.build_tree()

    # Cria tree_list
    def build_tree(self):
        # Cria um novo item derivado do item pai
        def fill_item(item: QTreeWidgetItem, data: list | dict, url_flag: bool = False):
            # Expande item
            item.setExpanded(True)

            # Verifica se o valor é um dicionário
            if type(data) is dict:
                for key, value in sorted(data.items(), key=sort_dict):
                    child = QTreeWidgetItem()

                    if key == 'urls':
                        key_parsed = 'URLS'
                        url_flag = True
                    elif key == 'no_artist':
                        key_parsed = 'Sem Artista'
                    else:
                        key_parsed = key.title()

                    child.setText(0, key_parsed)
                    item.addChild(child)

                    # Chama a função recursivamente
                    fill_item(child, value, url_flag)
            # Caso seja uma lista, itera sobre ela
            else:
                for value in data:
                    child = QTreeWidgetItem()

                    # Caso seja uma URL não formata a string
                    if not url_flag:
                        child.setText(0, value.title())
                    else:
                        child.setText(0, value)

                    item.addChild(child)

        # Limpa tree list
        self.tree_list.clear()

        # Libera botão de download caso haja dados
        if self.data:
            self.bt_download.setDisabled(False)
            fill_item(self.tree_list.invisibleRootItem(), self.data)
        else:
            self.bt_download.setDisabled(True)

    # Baixa lista do YouTube
    def download(self):
        # Verifica se o processo está em andamento
        if self.thread and self.thread.isRunning():
            Message.warning(self, 'ATENÇÃO', 'Já existe um processo em andamento, por favor aguarde.')
            return

        # Verifica se há conexão com a internet
        if not check_connection():
            Message.critical(self, 'CRÍTICO', 'Não há conexão com a internet.')
            return

        # Verifica se o usuário deseja prosseguir
        if Message.warning_question(self, 'Deseja fazer o download?') == Message.NO:
            return

        # Pega caminho para salvar
        self.path = QFileDialog.getSaveFileName(self, 'Salvar em', 'YT Downloader')[0]

        # Verifica se o caminho é válido
        if not self.path:
            Message.warning(self, 'ATENÇÃO', 'Nenhum diretório especificado.')
            return

        # Limpa o terminal
        self.txt_output.clear()

        # Prepara a thread que irá realizar os downloads
        self.thread = QThread()
        self.worker = Worker(self.data, self.path)
        self.worker.moveToThread(self.thread)

        # Conecta eventos
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.finished_thread)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.print_on_terminal.connect(self.print_on_terminal)

        # Inicia o download
        self.thread.start()

    # Printa no terminal informações
    def print_on_terminal(self, text: str):
        self.txt_output.append(text)

        # Move cursor para o fim do texto
        cursor = self.txt_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        self.txt_output.setTextCursor(cursor)

    # Elimina variáveis da memória e informa o usuário
    def finished_thread(self, force=False):
        # Elimina variáveis
        if self.thread and self.worker:
            self.thread.quit()
            self.thread.deleteLater()
            self.worker.deleteLater()
            self.thread = None

        # Informa o usuário que o processo terminou
        if not force:
            Message.information(self, 'AVISO', 'Download concluído.')

            # Abre a pasta de destino
            os.system(f'explorer {self.path}')

            # Reseta dados
            self.progress_bar.setValue(0)
            self.tree_list.clear()
            self.data.clear()

            self.bt_download.setDisabled(True)


# Usado para auxiliar na depuração
def exception_hook(exctype, value, traceback):
    sys.__excepthook__(exctype, value, traceback)
    sys.exit(1)


# Inicia o aplicativo
if __name__ == "__main__":
    # Evita bug no ícone na barra de tarefas quando compilado
    try:
        # noinspection PyUnresolvedReferences
        from ctypes import windll

        myappid = 'pc.youtube_downloader.3.0.1'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    sys.excepthook = exception_hook

    qt = QApplication(sys.argv)
    qt.setStyle('Fusion')
    qt.setWindowIcon(QIcon(os.path.join(BASEDIR, 'assets/icon-48.png')))

    app = App()
    app.show()

    sys.exit(qt.exec())
