from flask import render_template, session, redirect, url_for, current_app, request, flash
from .. import db
from ..models import User
# from ..email import send_email
from . import main
from .forms import AppApiForm, GetCompCSV, SelectCompCSV, MainForm
from .. import ISServer

import os
import sys
import csv
import glob
import datetime

import Tkinter as tk
import tkFileDialog
tk.Tk().withdraw()

startTimestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

companyExportFileName="Account.csv"
attachmentExportFileName="Attachment.csv"

DEFAULT_CONTACT_TO_ATTACH_TO = 1

homefolder = os.path.expanduser('~')
logfolder=os.path.abspath(os.path.join(homefolder, "Infusionsoft"))
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
logfile = os.path.abspath(os.path.join(logfolder, startTimestamp + "FileBoxUpload.csv"))

def getFilePath(titletext="Please select a file"):
    return tkFileDialog.askopenfilename(title=titletext)

def getFolderPath(titletext="Please select a folder"):
    return tkFileDialog.askdirectory(title=titletext)

def addtolog(rowdata):
    currentTimeStamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    with open(logfile, 'aUb+') as lfile:
        lfile.write(currentTimeStamp + "," + str(rawdata) + '\n')



@main.route('/', methods=['GET', 'POST'])
def index():
    neededdata = ["app",
                    "apikey",
                    "csvfolder",
                    "filesfolder",
                    "companyexport",
                    "contactexport",]
    for eachthing in neededdata:
        if eachthing not in session.keys():
            session[eachthing] = None
    form = MainForm()
    if form.is_submitted():
        session['app'] = form.app.data
        session['apikey'] = form.apikey.data
        if request.form["btn"] == "setcsvfolder":
            session['csvfolder'] = getFolderPath()
        if request.form["btn"] == "setfilesfolder":
            session['filesfolder'] = getFolderPath()
        if request.form["btn"] == "setcompanyexport":
            session['companyexport'] = getFilePath()
        if request.form["btn"] == "setcontactexport":
            session['contactexport'] = getFilePath()
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
            finally:
                pass
            if not thisconnection.verifyconnection():
                flash("There is a problem with the appname and API key. Please fix them.")
            # This is 2 - ensure that the files needed exist where they should be.
            filesincsvfolder = glob.glob(os.path.join(session['csvfolder'], "*"))
            for eachfilepath in filesincsvfolder:
                print eachfilepath
                print os.path.basename(eachfilepath)
                if os.path.basename(eachfilepath) == companyExportFileName:
                    hasOrigCompExp = True
                    OrigCompExp = eachfilepath
                if os.path.basename(eachfilepath) == attachmentExportFileName:
                    hasOrigAtthExp = True
                    OrigAtthExp = eachfilepath
            if not hasOrigCompExp:
                flash("I cannot find " + companyExportFileName + ".")
            if not hasOrigAtthExp:
                flash("I cannot find " + attachmentExportFileName + ".")
            # Part 3, Process the files.
            # Part 3a - match companyname to primarycontact
            infusionsoftCompanyByName = {}
            filesByAccountId = {}
            with open(session['companyexport'], 'rUb') as infile:
                companyreader = csv.DictReader(infile)
                for eachrow in companyreader:
                    if eachrow['Company'] in infusionsoftCompanyByName.keys():
                        addtolog(eachrow['Company'] + " already exists.")
                    thiscompany={}
                    thiscompany['contactFirstName'] = eachrow['Main Contact First Name']
                    thiscompany['contactLastName'] = eachrow['Main Contact Last Name']
                    infusionsoftCompanyByName[eachrow['Company']]={thiscompany}
            with open(OrigAtthExp, 'rUb') as attchIn:
                attchInReader = csv.DictReader(attchIn)
                for eachrow in attchInReader:
                    if eachrow['AccountId'] not in filesByAccountId.keys():
                        filesByAccountId[eachrow['AccountId']] = []
                    thisfilestuff = {}
                    thisfilestuff['fileid'] = eachrow['Id']
                    thisfilestuff['AccountId'] = eachrow['AccountId']
                    thisfilestuff['Name'] = eachrow['Name']
                    filesByAccountId[eachrow['AccountId']].append(thisfilestuff)
            for eachaccountid in filesByAccountId.keys():
                pass
                # with open(OrigCompExp, 'rUb') as

    return render_template('allonepage.html', form=form, app = session["app"], apikey = session["apikey"], csvfolder = session["csvfolder"], filesfolder = session["filesfolder"], companyexport = session["companyexport"], contactexport = session["contactexport"])

