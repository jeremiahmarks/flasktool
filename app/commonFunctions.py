#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: jeremiah.marks
# @Date:   2015-11-17 16:08:33
# @Last Modified by:   jeremiah.marks
# @Last Modified time: 2015-11-17 16:19:20


# This will house the commonly used
# functions that are not constrained within a blueprint.

import datetime
import Tkinter as tk
import tkFileDialog

startTimestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def getFilePath(titletext="Please select a file"):
    return tkFileDialog.askopenfilename(title=titletext)

def getFolderPath(titletext="Please select a folder"):
    return tkFileDialog.askdirectory(title=titletext)

def getTimeStamp(pattern='%Y%m%d%H%M%S'):
    return datetime.datetime.now().strftime(pattern)
