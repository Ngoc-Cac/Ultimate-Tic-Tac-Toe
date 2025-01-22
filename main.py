from PyQt6.QtWidgets import QApplication

from GUI.main_window import MainWindow

ult_tictactoe = QApplication([])
root = MainWindow(ult_tictactoe)

root.show()
ult_tictactoe.exec()