"""
NPG Popup Generator by Kevin Putra
Version: 1.0
Date: 11/FEB/2021
License: MIT
"""

from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QMainWindow, QApplication
from PySide2.QtCore import Qt, QThread, QTimer
from PySide2.QtGui import QIcon, QPixmap
from tkinter import filedialog, Tk
from configparser import ConfigParser
from popup_iterator import start_popup_iterator
import sys
import psutil
app = QApplication(sys.argv)
appcfg = ConfigParser()  # create new instance of ConfigParser
appcfg.read('configs/appsettings.ini', encoding='utf-8')  # read the app settings config file


class MainWindow(QMainWindow, QThread):  # Main Window Class
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("N.K Popup Generator v1.0 (" + "CPU Usage: " + str(psutil.cpu_percent()) + "%)")
        self.setMinimumWidth(600)
        self.setMinimumHeight(360)
        self.setWindowIcon(QIcon('configs/asset/appicon.png'))

        self.icon_file = None
        self.popup_preview = QtWidgets.QLabel(self)
        self.frame1 = QtWidgets.QFrame(self)
        self.frame2 = QtWidgets.QFrame(self)
        self.select_interval_label = QtWidgets.QLabel(self)
        self.select_interval = QtWidgets.QComboBox(self)
        self.custom_interval = QtWidgets.QLineEdit(self)
        self.num_of_popups_label = QtWidgets.QLabel(self)
        self.num_of_popups = QtWidgets.QLineEdit(self)
        self.error_popup = QtWidgets.QMessageBox()
        self.btn_browse_icon_label = QtWidgets.QLabel(self)
        self.btn_browse_icon = QtWidgets.QPushButton(self)
        self.popup_message_input = QtWidgets.QTextEdit(self)
        self.popup_title_input = QtWidgets.QLineEdit(self)
        self.popup_type_label = QtWidgets.QLabel(self)
        self.popup_type = QtWidgets.QComboBox(self)
        self.popup_style_label = QtWidgets.QLabel(self)
        self.popup_style = QtWidgets.QComboBox(self)
        self.btn_generate = QtWidgets.QPushButton(self)
        self.toggle_multiple_popups = QtWidgets.QCheckBox(self)
        self.cpu_stat_update_interval = QTimer(self)

        self.initui()
        self.update_preview()
        self.update_toggle_multiple_popups()
        self.change_interval_mode()

    def initui(self):
        self.frame1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame2.setFrameShape(QtWidgets.QFrame.StyledPanel)

        self.popup_title_input.setText(appcfg.get('popup_strings', 'popup_win_title'))
        self.popup_title_input.setAlignment(Qt.AlignCenter)
        self.popup_title_input.textChanged.connect(self.updatepopuptitle)
        self.popup_title_input.setToolTip("Edit your popup window title")

        self.popup_message_input.setText(appcfg.get('popup_strings', 'popup_message'))
        self.popup_message_input.textChanged.connect(self.updatepopupmessage)
        self.popup_message_input.setToolTip("Edit your popup message")

        self.popup_type_label.setText("PopUp Type:")
        self.popup_type_label.move(10, 100)
        popup_types = ['Info', 'Question', 'Warning', 'Critical']
        self.popup_type.addItems(popup_types)
        self.popup_type.setCurrentIndex(int(appcfg.get('popup_properties', 'popup_type_index')))
        self.popup_type.currentIndexChanged.connect(self.change_popup_type)
        self.popup_type.setToolTip("Choose the popup type")

        self.popup_style_label.setText("Popup Style:")
        self.popup_style_label.move(10, 50)
        popup_styles = ['Default', 'Fusion', 'Old']
        self.popup_style.addItems(popup_styles)
        self.popup_style.setCurrentIndex(int(appcfg.get('popup_properties', 'popup_style_index')))
        self.popup_style.setToolTip("Choose how you'd like your popup looks")
        self.popup_style.currentIndexChanged.connect(self.change_style)

        self.btn_browse_icon_label.setText("Popup Icon")
        self.btn_browse_icon_label.move(10, 0)
        self.btn_browse_icon.clicked.connect(self.get_icon_file)
        self.btn_browse_icon.setToolTip("Choose the popup window icon")
        self.btn_browse_icon.setText("Browse Icon")

        self.btn_generate.setText("Generate")
        self.btn_generate.setToolTip("Generate Popup")
        self.btn_generate.clicked.connect(self.generate_popup)
        self.change_style()

        self.toggle_multiple_popups.setText("Generate"
                                            "\nMultiple Popups")
        self.toggle_multiple_popups.setChecked(appcfg.getboolean('appconfig', 'generate_multiple_popups'))
        self.toggle_multiple_popups.clicked.connect(self.update_toggle_multiple_popups)
        self.toggle_multiple_popups.setToolTip("Enable/Disable multiple popup generation.")

        self.popup_preview.setPixmap(QPixmap('configs/asset/default_preview/default_info.PNG'))
        self.popup_preview.setToolTip("Popup Preview")

        self.num_of_popups_label.setText("Number of Popups:")
        self.num_of_popups.setText(appcfg.get('appconfig', 'number_of_multiple_popups'))
        self.num_of_popups.textChanged.connect(self.updatenumofpopups)
        self.num_of_popups.setAlignment(Qt.AlignCenter)
        self.num_of_popups.setToolTip("How much popups will be generated.")

        self.cpu_stat_update_interval.setInterval(appcfg.getint('appconfig', 'cpu_meter_update_interval'))
        self.cpu_stat_update_interval.start()
        self.cpu_stat_update_interval.timeout.connect(self.update_cpu_usage)

        self.select_interval_label.setText("Interval between"
                                           "\npopups:")
        interval_modes = ['Random', 'Custom']
        self.select_interval.addItems(interval_modes)
        self.select_interval.setCurrentIndex(appcfg.getint('appconfig', 'interval_between_popups_mode'))
        self.select_interval.currentIndexChanged.connect(self.change_interval_mode)
        self.select_interval.setToolTip("Select the interval type.")

        self.custom_interval.setAlignment(Qt.AlignCenter)
        self.custom_interval.setText(appcfg.get('appconfig', 'interval_between_popups'))
        self.custom_interval.textChanged.connect(self.update_custom_interval)
        self.custom_interval.setToolTip("Enter a custom interval between popups. (in seconds)")

    def change_interval_mode(self):
        appcfg.set('appconfig', 'interval_between_popups_mode', str(self.select_interval.currentIndex()))
        with open('configs/appsettings.ini', 'w', encoding='utf-8') as appconfig:
            appcfg.write(appconfig)

        if self.select_interval.currentIndex() == 0:
            self.custom_interval.setDisabled(True)
        else:
            self.custom_interval.setDisabled(False)

    def update_custom_interval(self):
        appcfg.set('appconfig', 'interval_between_popups', self.custom_interval.text())
        with open('configs/appsettings.ini', 'w', encoding='utf-8') as appconfig:
            appcfg.write(appconfig)

    def update_cpu_usage(self):
        self.setWindowTitle("N.K Popup Generator v1.0 (" + "CPU Usage: " + str(psutil.cpu_percent()) + "%)")

        #  called everytime the user changed the input value of the "Number of PopUps" input text field.
    def updatenumofpopups(self):  # write the new value of the Number of PopUps into the Config File
        appcfg.set('appconfig', 'number_of_multiple_popups', self.num_of_popups.text())
        with open('configs/appsettings.ini', 'w', encoding='utf-8') as appconfig:
            appcfg.write(appconfig)

        # called everytime the user changed the popup properties, e.g: style/type
    def update_preview(self):  # update the image preview according to the user's selected style/type
        if (self.popup_style.currentIndex() == 0) and (self.popup_type.currentIndex() == 0):
            self.popup_preview.setPixmap(QPixmap('configs/asset/default_preview/default_info.PNG'))
        elif (self.popup_style.currentIndex() == 0) and (self.popup_type.currentIndex() == 1):
            self.popup_preview.setPixmap(QPixmap('configs/asset/default_preview/default_question.PNG'))
        elif (self.popup_style.currentIndex() == 0) and (self.popup_type.currentIndex() == 2):
            self.popup_preview.setPixmap(QPixmap('configs/asset/default_preview/default_warning.PNG'))
        elif (self.popup_style.currentIndex() == 0) and (self.popup_type.currentIndex() == 3):
            self.popup_preview.setPixmap(QPixmap('configs/asset/default_preview/default_critical.PNG'))

        elif (self.popup_style.currentIndex() == 1) and (self.popup_type.currentIndex() == 0):
            self.popup_preview.setPixmap(QPixmap('configs/asset/fusion_preview/fusion_info.PNG'))
        elif (self.popup_style.currentIndex() == 1) and (self.popup_type.currentIndex() == 1):
            self.popup_preview.setPixmap(QPixmap('configs/asset/fusion_preview/fusion_question.PNG'))
        elif (self.popup_style.currentIndex() == 1) and (self.popup_type.currentIndex() == 2):
            self.popup_preview.setPixmap(QPixmap('configs/asset/fusion_preview/fusion_warning.PNG'))
        elif (self.popup_style.currentIndex() == 1) and (self.popup_type.currentIndex() == 3):
            self.popup_preview.setPixmap(QPixmap('configs/asset/fusion_preview/fusion_critical.PNG'))

        elif (self.popup_style.currentIndex() == 2) and (self.popup_type.currentIndex() == 0):
            self.popup_preview.setPixmap(QPixmap('configs/asset/old_preview/old_info.PNG'))
        elif (self.popup_style.currentIndex() == 2) and (self.popup_type.currentIndex() == 1):
            self.popup_preview.setPixmap(QPixmap('configs/asset/old_preview/old_question.PNG'))
        elif (self.popup_style.currentIndex() == 2) and (self.popup_type.currentIndex() == 2):
            self.popup_preview.setPixmap(QPixmap('configs/asset/old_preview/old_warning.PNG'))
        elif (self.popup_style.currentIndex() == 2) and (self.popup_type.currentIndex() == 3):
            self.popup_preview.setPixmap(QPixmap('configs/asset/old_preview/old_critical.PNG'))

    def update_toggle_multiple_popups(self):  # turn on/off multiple popups generation
        appcfg.set('appconfig', 'generate_multiple_popups', str(self.toggle_multiple_popups.isChecked()))
        if self.toggle_multiple_popups.isChecked():
            self.num_of_popups.setDisabled(False)
            self.num_of_popups_label.setDisabled(False)
            self.select_interval_label.setDisabled(False)
            self.select_interval.setDisabled(False)
            if self.select_interval.currentIndex() == 1:
                self.custom_interval.setDisabled(False)
        else:
            self.num_of_popups.setDisabled(True)
            self.num_of_popups_label.setDisabled(True)
            self.select_interval_label.setDisabled(True)
            self.select_interval.setDisabled(True)
            self.custom_interval.setDisabled(True)
        with open('configs/appsettings.ini', 'w', encoding='utf-8') as appconfig:
            appcfg.write(appconfig)

    def updatepopuptitle(self):
        appcfg.set('popup_strings', 'popup_win_title', self.popup_title_input.text())
        with open('configs/appsettings.ini', 'w', encoding='utf-8') as appconfig:
            appcfg.write(appconfig)

    def updatepopupmessage(self):
        appcfg.set('popup_strings', 'popup_message', self.popup_message_input.toPlainText())
        with open('configs/appsettings.ini', 'w', encoding='utf-8') as appconfig:
            appcfg.write(appconfig)

    def get_icon_file(self):
        root = Tk()
        root.withdraw()
        self.icon_file = filedialog.askopenfilename()
        appcfg.set('popup_properties', 'popup_icon_path', self.icon_file)
        with open('configs/appsettings.ini', 'w', encoding='utf-8') as appconfig:
            appcfg.write(appconfig)

    def change_style(self):
        if self.popup_style.currentIndex() == 0:
            app.setStyle('windowsvista')
        elif self.popup_style.currentIndex() == 1:
            app.setStyle('Fusion')
        elif self.popup_style.currentIndex() == 2:
            app.setStyle('Windows')

        appcfg.set('popup_properties', 'popup_style_index', str(self.popup_style.currentIndex()))
        with open('configs/appsettings.ini', 'w', encoding='utf-8') as appconfig:
            appcfg.write(appconfig)
        self.update_preview()

    def change_popup_type(self):
        appcfg.set('popup_properties', 'popup_type_index', str(self.popup_type.currentIndex()))
        with open('configs/appsettings.ini', 'w', encoding='utf-8') as appconfig:
            appcfg.write(appconfig)
        self.update_preview()

    def generate_popup(self):
        if appcfg.getboolean('appconfig', 'generate_multiple_popups'):
            start_popup_iterator()
        else:
            self.error_popup.setWindowTitle(self.popup_title_input.text())
            if self.popup_type.currentIndex() == 0:
                self.error_popup.setIcon(QtWidgets.QMessageBox.Information)
            elif self.popup_type.currentIndex() == 1:
                self.error_popup.setIcon(QtWidgets.QMessageBox.Question)
            elif self.popup_type.currentIndex() == 2:
                self.error_popup.setIcon(QtWidgets.QMessageBox.Warning)
            elif self.popup_type.currentIndex() == 3:
                self.error_popup.setIcon(QtWidgets.QMessageBox.Critical)
            self.error_popup.setText(self.popup_message_input.toPlainText())
            self.error_popup.setWindowIcon(QIcon(appcfg.get('popup_properties', 'popup_icon_path')))
            self.error_popup.exec_()

    def resizeEvent(self, event):
        self.frame1.setGeometry(QtCore.QRect(5, 5, self.width() - 470, 185))
        self.frame2.setGeometry(QtCore.QRect(self.width() - 460, 5, 100, 185))
        self.popup_title_input.setGeometry(10, 160, self.width() - 480, 25)
        self.popup_message_input.setGeometry(5, 195, self.width() - 10, self.height() - 200)
        self.btn_browse_icon.setGeometry(10, 25, self.width() - 520, 25)
        self.popup_type.setGeometry(10, 125, self.width() - 520, 25)
        self.popup_style.setGeometry(10, 75, self.width() - 520, 25)
        self.btn_generate.setGeometry(self.width() - 80, 165, 75, 25)
        self.popup_preview.setGeometry(self.width() - 315, 55, 265, 82)
        self.toggle_multiple_popups.move(self.width() - 455, 10)
        self.num_of_popups_label.move(self.width() - 455, 35)
        self.num_of_popups.setGeometry(self.width() - 455, 60, 90, 25)
        self.select_interval_label.move(self.width() - 455, 90)
        self.select_interval.setGeometry(self.width() - 455, 120, 90, 25)
        self.custom_interval.setGeometry(self.width() - 455, 160, 90, 25)


def window():
    global app
    win = MainWindow()
    win.show()

    sys.exit(app.exec_())


window()
