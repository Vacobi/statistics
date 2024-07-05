import sys
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtWidgets import QFileDialog

class statUI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('statistic.ui', self)
        self.data1 = []
        self.data2 = []
        self.openFileFirst.clicked.connect(self.first_file_load_signal)
        self.openFileSecond.clicked.connect(self.second_file_load_signal)
        self.calculateButton.clicked.connect(self.define_samples_type)

    def load_text_file(widget):
        filter = 'Текстовые файлы (*.txt);; Все файлы (*.*)'
        filename = QFileDialog.getOpenFileName(widget, 'Выберите файл', filter=filter)

        if filename[0] != '':
            widget.currentFile = filename[0]
            widget.selectedFile.setText(widget.currentFile)

    def parse_sample_file(self, filename):
        data = []
        current_token = ""
        with open(filename, encoding="utf-8") as fobj:
            while True:
                char = fobj.read(1)
                if not char:
                    break

                if not char.isdigit() and char not in "-., " and not char.isspace():
                    raise ValueError("Неверный символ в файле выборки")

                if not char.isspace():
                    current_token += char
                else:
                    if "," in current_token or "." in current_token:
                        data.append(float(current_token.replace(",", ".")))
                    elif current_token:
                        data.append(int(current_token))
                    current_token = ""
        if current_token:
            if "," in current_token or "." in current_token:
                data.append(float(current_token.replace(",", ".")))
            else:
                data.append(int(current_token))
        return data

    def first_file_load_signal(self):
        filter = 'Текстовые файлы (*.txt);; Все файлы (*.*)'
        filename = QFileDialog.getOpenFileName(self, 'Выберите файл', filter=filter)

        if filename[0] != '':
            self.data1 = self.parse_sample_file(filename[0])

    def second_file_load_signal(self):
        filter = 'Текстовые файлы (*.txt);; Все файлы (*.*)'
        filename = QFileDialog.getOpenFileName(self, 'Выберите файл', filter=filter)

        if filename[0] != '':
            self.data2 = self.parse_sample_file(filename[0])

    def define_samples_type(self):
        try:
            if len(self.data1) == 0:
                raise ValueError('Файл с первым распределнием не выбран или пуст\n')
        except ValueError as err:
            QMessageBox.warning(self, 'Ошибка!', str(err))
            return None

        try:
            if len(self.data2) == 0:
                raise ValueError('Файл со вторым распределнием не выбран или пуст\n')
        except ValueError as err:
            QMessageBox.warning(self, 'Ошибка!', str(err))
            return None


    def distribution_normal(data = []):
        try:
            if data == 0:
                raise ValueError()
        except ValueError as err:
            return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = statUI()
    window.show()
    sys.exit(app.exec_())

