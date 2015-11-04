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
import base64


import Tkinter as tk
import tkFileDialog
tk.Tk().withdraw()

infusionsoftCompanyToMainContactId={}
salesforceAccountIdToInfMainContactId={}

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

def addtolog(datatoadd):
    currentTimeStamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    with open(logfile, 'ab+') as lfile:
        lfile.write(currentTimeStamp + "," + str(datatoadd) + '\n')

def getprimarycontactid(connection, companyExportRow):
    """This method aims to accept a row of data from a
    Company export of Infusionsoft and match the name to a
    contact id.  It will do this by pulling all records that
    have company id == to the rows company id as well as matching
    fname/lname data.

    If there are multiple matching records, it will go with
    the oldest record, unless the fields are blank, in which
    case it will go with the DEFAULT_CONTACT_TO_ATTACH_TO
    """
    # if companyExportRow['Main Contact First Name'] and companyExportRow['Main Contact Last Name']:
    if not ((companyExportRow['Main Contact First Name'] and len(companyExportRow['Main Contact First Name'])>0)
            or (companyExportRow['Main Contact Last Name'] and len(companyExportRow['Main Contact Last Name']) > 0)):
        searchcriteria = {}
        searchcriteria["CompanyID"] = companyExportRow['Id']
        if companyExportRow['Main Contact First Name'] and len(companyExportRow['Main Contact First Name']) > 0:
            searchcriteria['FirstName'] = companyExportRow['Main Contact First Name']
        if companyExportRow['Main Contact Last Name'] and len(companyExportRow['Main Contact Last Name']) > 0:
            searchcriteria['LastName'] = companyExportRow['Main Contact Last Name']
        allmatchingcontacts = connection.getallrecords('Contact', searchcriteria=searchcriteria, orderedby="Id")
        if len(allmatchingcontacts) == 0:
            return DEFAULT_CONTACT_TO_ATTACH_TO
        elif len(allmatchingcontacts) == 1:
            return allmatchingcontacts[0]['Id']
        else:
            return allmatchingcontacts[0]['Id']
    else:
        return DEFAULT_CONTACT_TO_ATTACH_TO

def matchSFIDtoInfId(salesforceAccountId, pathToCompFile):
    """This method will accept a row of data from the
    attachments export as well as the path to the
    companyExportFileName. It will check to see if their is
    an existing match in a global dictionary. If there is
    it will return the ContactId
    """
    if salesforceAccountId in salesforceAccountIdToInfMainContactId.keys():
        print "Yay, it is matched!"
        return salesforceAccountIdToInfMainContactId[salesforceAccountId]
    else:
        with open(pathToCompFile, 'rUb') as infile:
            thisreader = csv.DictReader(infile)
            for eachrow in thisreader:
                if eachrow["Id"] == salesforceAccountId:
                    thiscompname = eachrow["Name"]
                    if thiscompname in infusionsoftCompanyToMainContactId.keys():
                        print "This is that thing!"
                        print infusionsoftCompanyToMainContactId[thiscompname]
                        print thiscompname
                        salesforceAccountIdToInfMainContactId[salesforceAccountId] = infusionsoftCompanyToMainContactId[thiscompname]
                    else:
                        salesforceAccountIdToInfMainContactId[salesforceAccountId] = DEFAULT_CONTACT_TO_ATTACH_TO
                        addtolog("Count not find " + salesforceAccountId + " " + thiscompname)
                    break
            else:
                addtolog("Could not find " + salesforceAccountId + " in the compexport")
                salesforceAccountIdToInfMainContactId[salesforceAccountId] = DEFAULT_CONTACT_TO_ATTACH_TO
        return salesforceAccountIdToInfMainContactId[salesforceAccountId]

# def attachfile(eachrow, contactIdToAttachTo, session['filesfolder'], thisconnection)
def attachfile(eachrow, contactIdToAttachTo, pathToFolder, thisconnection):
    """This method accepts a row of data from a salesforce
    Attachment.csv file, an Infusionsoft Contact Id, the
    path to the folder that actually has all of the blobs,
    and an API connection.
    """
    blobname = eachrow['Id']
    print "attaching " + blobname + " to " + str(contactIdToAttachTo)
    pathtoblob = os.path.abspath(os.path.join(pathToFolder, blobname))
    # print "ER: " + str(eachrow)
    print "PATHTOBLOB: " + pathtoblob
    print thisconnection.connection.FileService.uploadFile(thisconnection.infusionsoftapikey, contactIdToAttachTo, eachrow['Name'], base64.b64encode(open(pathtoblob, 'rUb').read()))


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
            infusionsoftCompanyToMainContactId = {}
            filesByAccountId = {}
            accountIdToCompanyName={}
            with open(session['companyexport'], 'rUb') as infile:
                companyreader = csv.DictReader(infile)
                for eachrow in companyreader:
                    if eachrow['Company'] in infusionsoftCompanyToMainContactId.keys():
                        addtolog(eachrow['Company'] + " already exists.")
                    infusionsoftCompanyToMainContactId[eachrow['Company']]=getprimarycontactid(thisconnection, eachrow)
            with open(OrigAtthExp, 'rUb') as attchIn:
                attchInReader = csv.DictReader(attchIn)
                for eachrow in attchInReader:
                    contactIdToAttachTo = matchSFIDtoInfId(eachrow['AccountId'], OrigCompExp)
                    attachfile(eachrow, contactIdToAttachTo, session['filesfolder'], thisconnection)

            #         if eachrow['AccountId'] not in filesByAccountId.keys():
            #             filesByAccountId[eachrow['AccountId']] = []
            #         thisfilestuff = {}
            #         thisfilestuff['fileid'] = eachrow['Id']
            #         thisfilestuff['AccountId'] = eachrow['AccountId']
            #         thisfilestuff['Name'] = eachrow['Name']
            #         filesByAccountId[eachrow['AccountId']].append(thisfilestuff)
            # for eachaccountid in filesByAccountId.keys():
            #     with open(OrigCompExp, 'rUb') as infile:
            #         yetAnotherReader = csv.DictReader(infile)
            #         for eachrow in yetAnotherReader:
            #             if eachrow['Id'] == eachaccountid:
            #                 accountIdToCompanyName[eachaccountid] = {}
            #                 accountIdToCompanyName[eachaccountid]['Name'] = eachrow['Name']
            #                 break
            # for eachaccountid in filesByAccountId.keys():
            #     companyname = accountIdToCompanyName[eachaccountid]['Name']
            #     if 'primaryContact' in accountIdToCompanyName[eachaccountid].keys():
            #         contactid = accountIdToCompanyName[eachaccountid]['primaryContact']
            #     else:
            #         if companyname in infusionsoftCompanyByName.keys():
            #             fname = infusionsoftCompanyByName[companyname]['contactFirstName']
            #             lname = infusionsoftCompanyByName[companyname]['contactLastName']
            #     # with open(OrigCompExp, 'rUb') as

    return render_template('allonepage.html', form=form, app = session["app"], apikey = session["apikey"], csvfolder = session["csvfolder"], filesfolder = session["filesfolder"], companyexport = session["companyexport"], contactexport = session["contactexport"])

