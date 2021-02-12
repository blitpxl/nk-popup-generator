"""
This script is meant to be iterated many times to replicate the spawning of many error popups.
"""

from PySide2 import QtWidgets
import random
from PySide2.QtWidgets import QMainWindow, QApplication
from PySide2.QtGui import QIcon
from configparser import ConfigParser
import sys
app = QApplication(sys.argv)
appcfg = ConfigParser()
appcfg.read('configs/appsettings.ini')

if appcfg.getint('popup_properties', 'popup_style_index') == 0:
    app.setStyle('windowsvista')
elif appcfg.getint('popup_properties', 'popup_style_index') == 1:
    app.setStyle('Fusion')
elif appcfg.getint('popup_properties', 'popup_style_index') == 2:
    app.setStyle('Windows')


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.msg = QtWidgets.QMessageBox(self)
        self.msg.setWindowTitle(appcfg.get('popup_strings', 'popup_win_title'))
        self.msg.setText(appcfg.get('popup_strings', 'popup_message'))
        self.msg.move(random.randint(0, 1000), random.randint(0, 600))
        if appcfg.getint('popup_properties', 'popup_type_index') == 0:
            self.msg.setIcon(QtWidgets.QMessageBox.Information)
        elif appcfg.getint('popup_properties', 'popup_type_index') == 1:
            self.msg.setIcon(QtWidgets.QMessageBox.Question)
        elif appcfg.getint('popup_properties', 'popup_type_index') == 2:
            self.msg.setIcon(QtWidgets.QMessageBox.Warning)
        elif appcfg.getint('popup_properties', 'popup_type_index') == 3:
            self.msg.setIcon(QtWidgets.QMessageBox.Critical)
        self.setWindowIcon(QIcon(appcfg.get('popup_properties', 'popup_icon_path')))
        self.msg.exec_()
        sys.exit()


def window():
    global app
    MainWindow()

    sys.exit(app.exec_())


window()
