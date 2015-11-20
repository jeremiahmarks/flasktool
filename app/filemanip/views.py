from flask import render_template, session, redirect, url_for, current_app, request, flash
from .. import db
from ..models import User
# from ..email import send_email
from . import csvBP as main
from .forms import FileForm
from .. import ISServer
from .. import fileprocessor
from .. import commonFunctions as funcs

import os
import sys
import csv
import glob
import datetime
import base64
import pickle


startTimestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

homefolder = os.path.expanduser('~')
logfolder=os.path.abspath(os.path.join(homefolder, "Infusionsoft"))
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
logfile = os.path.abspath(os.path.join(logfolder, startTimestamp + "FileBoxUpload.csv"))


def addtolog(datatoadd):
    currentTimeStamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    with open(logfile, 'ab+') as lfile:
        lfile.write(currentTimeStamp + "," + str(datatoadd) + '\n')

@main.route('/', methods=['GET', 'POST'])
def index():
    neededdata=['file1', 'file2']
    for eachdatum in neededdata:
        if neededdata not in session.keys():
            session[eachdatum] = None
    form = FileForm()
    if form.is_submitted():
        if request.form["btn"] == "setfile1":
            session['file1'] = funcs.getFilePath()
        if request.form["btn"] == "setfile2":
            session['file2'] = funcs.getFilePath()
    return render_template('vlookup.html', form=form, file1=session['file1'], file2=session['file2'])

@main.route('/files', methods=['GET', 'POST'])
def start():
    # return redirect(url_for('csv_blueprint.index'))
    neededdata=['file1', 'file2']
    for eachdatum in neededdata:
        if neededdata not in session.keys():
            session[eachdatum] = None
    form = FileForm()
    if form.is_submitted():
        if request.form["btn"] == "setfile1":
            session['file1'] = funcs.getFilePath()
        if request.form["btn"] == "setfile2":
            session['file2'] = funcs.getFilePath()
    return render_template('vlookup.html', form=form, file1=session['file1'], file2=session['file2'])
