"""
This script is meant to iterate the popup window process
to replicate the spawning of many popups errors.
This script will iterate the popup script until the threshold is reached.
"""

import subprocess
import time
from configparser import ConfigParser
import random

appcfg = ConfigParser()
appcfg.read('configs/appsettings.ini', encoding='utf-8')

i = 0


def start_popup_iterator():
    appcfg.read('configs/appsettings.ini', encoding='utf-8')

    global i
    while i < appcfg.getint('appconfig', 'number_of_multiple_popups'):
        subprocess.Popen('iterable_popup.py', shell=True)  # iterate the iterable popup
        if appcfg.getint('appconfig', 'interval_between_popups_mode') == 0:
            interval_between_popups = random.random()
        else:
            interval_between_popups = appcfg.getfloat('appconfig', 'interval_between_popups')
        time.sleep(interval_between_popups)
        i += 1
    i = 0
