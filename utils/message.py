import functools

from PyQt6.QtWidgets import QMessageBox


class Message(QMessageBox):
    """Template de QMessageBox com captions personalizados para botões"""
    YES = QMessageBox.StandardButton.Yes
    NO = QMessageBox.StandardButton.No

    def __init__(
            self,
            parent=None,
            buttons: list[tuple[QMessageBox.StandardButton, str]] | None = None,
    ):
        super().__init__(parent)

        if buttons:
            self.set_caption_buttons(buttons)

    @classmethod
    def warning_question(cls, parent, message: str, default_button=QMessageBox.StandardButton.No) -> int:
        """
        Cria e executa uma message box de aviso com botões de Sim e Não.

        :param parent: Parent
        :param message: Mensagem para exibir
        :param default_button: Botão padrão
        :return: Resposta do usuário
        """
        buttons = [(QMessageBox.StandardButton.Yes, 'Sim'), (QMessageBox.StandardButton.No, 'Não')]

        self = cls(parent, buttons)
        answer = self.show_message(
            'ATENÇÃO',
            message,
            QMessageBox.Icon.Warning,
            default_button
        )

        return answer

    def show_message(
            self,
            title: str,
            message: str,
            icon: QMessageBox.Icon | None = None,
            default_button: QMessageBox.StandardButton | None = None
    ) -> int:
        """
        Exibe a MessageBox.

        :param title: Título do popup
        :param message: Mensagem do popup
        :param icon: Ícone do popup
        :param default_button: Botão padrão
        :return: Resposta do usuário
        """
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(icon)
        self.setDefaultButton(default_button)

        return super().exec()

    def set_caption_buttons(self, buttons: list[tuple[QMessageBox.StandardButton, str]]):
        """
        Seta captions personalizados.

        :param buttons: Lista contendo tuplas, sendo o primeiro valor o Enum do botão e o segundo o caption
        """
        b = functools.reduce(lambda b, button: b | button[0], buttons, 0)
        self.setStandardButtons(b)

        for button, caption in buttons:
            self.button(button).setText(caption)
