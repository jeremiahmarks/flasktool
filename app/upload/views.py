from flask import render_template, session, redirect, url_for, current_app, request, flash
from .. import db
from ..models import User
# from ..email import send_email
from . import main
from .forms import AppApiForm, GetCompCSV, SelectCompCSV, MainForm
from .. import ISServer
from .. import fileprocessor

import os
import sys
import csv
import glob
import datetime
import base64
import pickle

import Tkinter as tk
import tkFileDialog
tk.Tk().withdraw()


startTimestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

homefolder = os.path.expanduser('~')
logfolder=os.path.abspath(os.path.join(homefolder, "Infusionsoft"))
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
logfile = os.path.abspath(os.path.join(logfolder, startTimestamp + "FileBoxUpload.csv"))

def getFilePath(titletext="Please select a file"):
    return tkFileDialog.askopenfilename(title=titletext)

def getFolderPath(titletext="Please select a folder"):
    return tkFileDialog.askdirectory(title=titletext)

def addtolog(datatoadd):
    currentTimeStamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    with open(logfile, 'ab+') as lfile:
        lfile.write(currentTimeStamp + "," + str(datatoadd) + '\n')

@main.route('/', methods=['GET', 'POST'])
def index():
    neededdata = ["app",
                    "apikey",
                    "accountCSV",
                    "filesfolder",
                    "companyexport",
                    "attachmentCSV",]
    for eachthing in neededdata:
        if eachthing not in session.keys():
            session[eachthing] = None
    form = MainForm()
    print session
    if form.is_submitted():
        session['app'] = form.app.data
        session['apikey'] = form.apikey.data
        if request.form["btn"] == "setaccountCSV":
            session['accountCSV'] = getFilePath()
        if request.form["btn"] == "setattachmentCSV":
            session['attachmentCSV'] = getFilePath()
        if request.form["btn"] == "setcompanyexport":
            session['companyexport'] = getFilePath()
        if request.form["btn"] == "setfilesfolder":
            session['filesfolder'] = getFolderPath()


        print "A"
        if request.form['btn'] == "VerifyAndUpload":
            """
                How to verify and upload, in this case:
                1. ensure that the appname and apikey are good.
                2. ensure that the required files are there.
                3. process the files
                    in order to process the files, one will:
                        match companyname to primarycontact
                        match primarycontact to contactid
                        for eachline in session['csvfolder'].Attachment.csv
                            match AccountId to AccountName
                            match AccountName to ContactId via CompanyName
            """
            hasOrigCompExp = False
            OrigCompExp = ""
            hasOrigAtthExp = False
            OrigAtthExp = ""
            # This is the start of part1, basically verifying that the connection can connect
            try:
                thisconnection = ISServer.ISServer(session['app'], session['apikey'])
            except Exception, e:
                addtolog(str(Exception))
                addtolog(str(e))
                flash(message)
            if not thisconnection.verifyconnection():
                flash("There is a problem with the appname and API key. Please fix them.")
            # This is 2 - ensure that the files needed exist where they should be.
            # connection = ISServer.ISServer('if188', 'f1a4ac7f9dbe2341ad0b84b52581c93e')
            # logic = FileLogician(connection)
            # logic.setAccount('C:\\Users\\jeremiah.marks\\Desktop\\actCrap\\if188\\Account.csv')
            # logic.setAttachment('C:\\Users\\jeremiah.marks\\Desktop\\actCrap\\if188\\Attachment.csv')
            # logic.setexport('C:\\Users\\jeremiah.marks\\Desktop\\actCrap\\if188\\companyexport.csv')
            # logic.setfilefolder('C:\\Users\\jeremiah.marks\\Desktop\\actCrap\\if188\\files')
            # logic.startToProcess()

            thisprocessor = fileprocessor.FileLogician(thisconnection)
            thisprocessor.setAccount(session['accountCSV'])
            thisprocessor.setAttachment(session['attachmentCSV'])
            thisprocessor.setexport(session['companyexport'])
            thisprocessor.setfilefolder(session['filesfolder'])
            thisprocessor.startToProcess()

    return render_template('allonepage.html', form=form, app = session["app"], apikey = session["apikey"], accountCSV = session["accountCSV"], filesfolder = session["filesfolder"], companyexport = session["companyexport"], attachmentCSV = session["attachmentCSV"])

