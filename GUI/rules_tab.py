from PyQt6.QtWidgets import (
    QLabel,
    QWidget
)

class Rules(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel(r"¯\_(ツ)_/¯", parent=self)