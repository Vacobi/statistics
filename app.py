import sys
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtWidgets import QFileDialog

import math
import numpy as np
from scipy.stats import shapiro #Тест Шапиро-Уилка
from scipy.stats import kstest #Тест Колмогорова-Смирнова
from scipy.stats import ttest_ind #Тест t-критерий Стьюдента для независимых выборок
from scipy.stats import ttest_rel #Тест t-критерий Стьюдента для зависимых выборок
from scipy.stats import mannwhitneyu #Тест Манна-Уитни для независимых выборок
from scipy.stats import wilcoxon #Тест t-критерий Вилкоксона для зависимых выборок

class statUI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('statistic.ui', self)
        self.data1 = []
        self.data2 = []
        self.openFileFirst.clicked.connect(self.first_file_load_signal)
        self.openFileSecond.clicked.connect(self.second_file_load_signal)
        self.calculateButton.clicked.connect(self.define_sample_type_and_calculate_test)

    def define_sample_type_and_calculate_test(self):
        if (self.define_samples_type() != None):
            self.calculate_test()


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
        filter = 'Текстовые файлы (*.txt); Все файлы (*.*)'
        filename = QFileDialog.getOpenFileName(self, 'Выберите файл', filter=filter)

        if filename[0] != '':
            try:
                data = self.parse_sample_file(filename[0])
            except ValueError as err:
                QMessageBox.warning(self, 'Ошибка!', str(err))
                return None
            self.data1 = np.array(data)
            self.selectedFileFirst.setText(filename[0])


    def second_file_load_signal(self):
        filter = 'Текстовые файлы (*.txt); Все файлы (*.*)'
        filename = QFileDialog.getOpenFileName(self, 'Выберите файл', filter=filter)

        if filename[0] != '':
            try:
                data = self.parse_sample_file(filename[0])
            except ValueError as err:
                QMessageBox.warning(self, 'Ошибка!', str(err))
                return None
            self.data2 = np.array(data)
            self.selectedFileSecond.setText(filename[0])

    def define_samples_type(self):
        try:
            self.firstIsNormal = self.distribution_normal(self.data1)
        except ValueError as err:
            QMessageBox.warning(self, 'Ошибка!', str('Файл с первым распределнием не выбран или пуст\n'))
            return None

        if self.firstIsNormal:
            self.firstSampleDistributed.setText('нормально')
        else:
            self.firstSampleDistributed.setText('ненормально')

        try:
            self.secondIsNormal = self.distribution_normal(self.data2)
        except ValueError as err:
            QMessageBox.warning(self, 'Ошибка!', str('Файл со вторым распределнием не выбран или пуст\n'))
            return None

        if self.secondIsNormal:
            self.secondSampleDistributed.setText('нормально')
        else:
            self.secondSampleDistributed.setText('ненормально')

        return 1


    def distribution_normal(self, data = ()):
        if len(data) == 0:
            raise ValueError('')

        if len(data) < 50:
            stat, p = shapiro(data)

            alpha = 0.05
            if p > alpha:
                return True
            else:
                return False
        else:
            stat, p = kstest(data, "norm", alternative='less')

            alpha = 0.05
            if p > alpha:
                return True
            else:
                return False

    def calculate_test(self):
        self.dependentSamples = self.dependentSamplesCheckbox.isChecked()

        if self.firstIsNormal and self.secondIsNormal:
            self.typeOfTests.setText('параметрические')

            if self.dependentSamples:
                try:
                    value = self.calculate_t_Student_for_related()
                    resultOfTest = value.statistic
                    nameOfTest = 't-критерий Стьюдента для зависимых выборок'
                    text_description = '(используется для определения статистической значимости различий средних величин)'
                    null_hypotes = '(нулевая гипотеза предполагает, что средние значения распределений, лежащих в основе выборок, равны)'
                except ValueError as err:
                    QMessageBox.warning(self, 'Ошибка!', str(err))
                    return None
            else:
                value = self.calculate_t_Student_for_independent()
                resultOfTest = value.statistic
                nameOfTest = 't-критерий Стьюдента для независимых выборок'
                text_description = '(используется для определения статистической значимости различий средних величин)'
                null_hypotes = '(нулевая гипотеза предполагает, что средние значения распределений, лежащих в основе выборок, равны)'
        else:
            self.typeOfTests.setText('непараметрические')

            if self.dependentSamples:
                try:
                    value = self.calculate_wilcoxon()
                    resultOfTest = value.statistic
                    nameOfTest = 't-критерий Вилкоксона'
                    text_description = '(используется для оценки различий между двумя рядами измерений)'
                    null_hypotes = '(нулевая гипотеза предполагает, что медианы разностей равны нулю, то есть нет значимых различий между выборками)'
                except ValueError as err:
                    QMessageBox.warning(self, 'Ошибка!', str(err))
                    return None
            else:
                value = self.calculate_mannwhitneyu()
                resultOfTest = len(self.data1) * len(self.data2) - value.statistic
                nameOfTest = 'критерий Манна-Уитни'
                text_description = '(используется для оценки различий между двумя независимыми выборками по уровню какого-либо признака, измеренного количественно)'
                null_hypotes = '(нулевая гипотеза предполагает, что распределения приблизительно равны)'

        self.resultOfTest.setValue(resultOfTest)
        self.probability.setValue(value.pvalue)
        self.testName.setText(nameOfTest)
        self.description.setText(text_description)

        if (value.pvalue > 0.05):
            self.hypoteses_result.setText('Нулевая гипотеза принимается ' + null_hypotes)
        else:
            self.hypoteses_result.setText('Нулевая гипотеза отвергается ' + null_hypotes)

    def calculate_t_Student_for_related(self):
        if len(self.data1) != len(self.data2):
            raise ValueError('Невозможно выполнить тест "t-критерий Стьюдента для зависимых выборок", так как ' +
                             'размеры выборок не совпадают: в первой выборке содержится ' + str(len(self.data1)) +
                             ' элементов, в то время как во второй ' + str(len(self.data2)) + ' элементов')

        return ttest_rel(self.data1, self.data2)

    def calculate_t_Student_for_independent(self):
        return ttest_ind(self.data1, self.data2)

    def calculate_mannwhitneyu(self):
        return mannwhitneyu(self.data1, self.data2)

    def calculate_wilcoxon(self):
        if len(self.data1) != len(self.data2):
            raise ValueError('Невозможно выполнить тест "t-критерий Вилкоксона", так как ' +
                             'размеры выборок не совпадают: в первой выборке содержится ' + str(len(self.data1)) +
                             ' элементов, в то время как во второй ' + str(len(self.data2)) + ' элементов')

        return wilcoxon(self.data1, self.data2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = statUI()
    window.show()
    sys.exit(app.exec_())

