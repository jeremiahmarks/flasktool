#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: jeremiah.marks
# @Date:   2015-11-17 16:08:33
# @Last Modified by:   jeremiah.marks
# @Last Modified time: 2015-11-18 21:39:01


# This will house the commonly used
# functions that are not constrained within a blueprint.

import datetime
import Tkinter as tk
import tkFileDialog
import os

options = {}
options['defaultextension'] = '.csv'
options['filetypes'] = [('migration', '*.csv'), ('Things supported by excel so: maybe, someday?', ('*.bmp','*.bmp ','*.csv','*.dbf','*.dif','*.doc','*.emf','*.gif','*.htm','*.jpg','*.ods','*.prn','*.rtf','*.slk','*.txt','*.wmf','*.xla','*.xlam','*.xls','*.xlsb','*.xlsm','*.xlsx','*.xlt','*.xltm','*.xltx','*.xlw','*.xml')), ('all files', '.*')]
options['initialdir'] = os.path.abspath(os.path.expanduser('~'))


startTimestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def getFilePath(titletext="Please select a file"):
    return tkFileDialog.askopenfilename(title=titletext, **options)

def getFolderPath(titletext="Please select a folder"):
    return tkFileDialog.askdirectory(title=titletext, **options)

def getTimeStamp(pattern='%Y%m%d%H%M%S'):
    return datetime.datetime.now().strftime(pattern)
