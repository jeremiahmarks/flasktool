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
import pickle

import Tkinter as tk
import tkFileDialog
tk.Tk().withdraw()

infusionsoftCompanyToMainContactId={}
salesforceAccountIdToInfMainContactId={}

startTimestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

salesforceaccountfile="Account.csv"
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




# create a place to map salesforce AccountIDs to contactIds
salesforceAccountIdToInfusionsoftContactId={}
sfids=salesforceAccountIdToInfusionsoftContactId

# create a variable to hold the path to the file that the customer exported
###        ###
###  TO DO ###
###        ###
### make sure to add exported file to the main method as a global. 
exportedfile=''

def getmatchingrows(filename, columnname, value):
    """This method will return a list of csv rows
    that have the matching value in the named
    column.
    """
    matchingrows=[]
    if filename and len(filename)==0:
        print columnname, value
        print """NameError('whoa nelly! you cannot use' + str(filename))"""
    else:
        try:
            with open(filename, 'rUb') as infile:
                thisreader = csv.DictReader(infile)
                if columnname not in thisreader.fieldnames:
                    print "Error, attempted to find value %s in column '%s' of file '%s'" %(value, columnname, filename)
                else:
                    for eachrow in thisreader:
                        if eachrow[columnname] == value:
                            matchingrows.append(eachrow)
        except Exception, e:
            print Exception
        finally:
            return matchingrows

def pickACompanyrecord(listOfCompaniesWithSameName):
    """This method exists in case there are multiple
    companies with the same name.  If there are, this
    method will pick first by existance of a primary
    contact, then, all other things being equal, 
    by the lowest ID
    """
    print type(listOfCompaniesWithSameName)
    print listOfCompaniesWithSameName
    # bestmatch=listOfCompaniesWithSameName[0]
    # for eachrecord in listOfCompaniesWithSameName:
    #     if eachrecord['Main Contact First Name'] and eachrecord['Main Contact Last Name']:
    #         if eachrecord['Id'] < bestmatch['Id']:
    #             bestmatch=eachrecord
    #         else:
    #             if not  bestmatch['Main Contact First Name'] and bestmatch['Main Contact Last Name']:
    #                 bestmatch=eachrecord
    #                 # Basically, how this works is:
    #                     # since we are evaluating using 'and' this means that if there is anything in the value
    #                     # it is true. If there is not (or it is literally False, but duck typing)
    #                     # the expression will evaluate to false.
    #                     #
    #                     # So what we are saying is "If best match does not have both a first name and a last name
    #                     # then this is already a superior contact because it does have both"
    #     elif bestmatch['Main Contact First Name'] and bestmatch['Main Contact Last Name']:
    #         # we know that the record has one or none of the fn/ln
    #         # that means that if the bestmatch has both, we are done
    #         pass
    #     # from here, we know that neither record has both names.
    #     # Basically, this should be:  
    #         # if either one has at least one value as well as a lower id, it is the best value.
    #     elif bestmatch['Main Contact First Name'] or bestmatch['Main Contact Last Name']:
    #         if bestmatch['Id']>eachrecord['Id']:
    #             bestmatch = eachrecord['Id']
    # return bestmatch


def matchsfAccountIdtocontactid(salesforceaccountid, basefolder, apiconnection):
    """This method use the getmatchingrows method to 
    find the rows that match what they need to match.
    """
    print "a1"
    global exportedfile
    accountpath = os.path.join(basefolder, salesforceaccountfile)
    matchingSFAccounts = getmatchingrows(accountpath, 'Id', salesforceaccountid)
    if not matchingSFAccounts:
        return DEFAULT_CONTACT_TO_ATTACH_TO
    elif len(matchingSFAccounts)==0:
        return DEFAULT_CONTACT_TO_ATTACH_TO
    else:
        if len(matchingSFAccounts) > 1:
            print "There is an error. There appear to be multiple records with the id " + str(salesforceaccountid)
            return DEFAULT_CONTACT_TO_ATTACH_TO
        else:
            companyname = matchingSFAccounts[0]["Name"]
            matchingInfusionsoftcompanies = getmatchingrows(exportedfile, 'Company', companyname)
            if matchingInfusionsoftcompanies and len(matchingInfusionsoftcompanies) == 0:
                return DEFAULT_CONTACT_TO_ATTACH_TO
            selectedCompanyRecord=pickACompanyrecord(matchingInfusionsoftcompanies)
            searchcriteria={}
            if selectedCompanyRecord:
                if 'Id' in selectedCompanyRecord.keys():
                    searchcriteria['CompanyID'] = selectedCompanyRecord['Id']
                if selectedCompanyRecord['Main Contact First Name']:
                    searchcriteria['FirstName'] = selectedCompanyRecord['Main Contact First Name']
                if selectedCompanyRecord['Main Contact Last Name']:
                    searchcriteria['LastName'] = selectedCompanyRecord['Main Contact Last Name']
                matchingcontacts=apiconnection.getallrecords('Contact', searchcriteria=searchcriteria, interestingdata=['Id'], orderedby='Id')
                print searchcriteria
                if matchingcontacts and len(matchingcontacts) == 0:
                    return DEFAULT_CONTACT_TO_ATTACH_TO
                else:
                    return matchingcontacts[0]
            else:
                return DEFAULT_CONTACT_TO_ATTACH_TO

def attachfile(pathtofile, nameToUploadAs, contactIdToAttachTo, apiConnectionToUse):
    print apiConnectionToUse.connection.FileService.uploadFile(apiConnectionToUse.infusionsoftapikey, contactIdToAttachTo, nameToUploadAs, base64.b64encode(open(pathtofile, 'rUb').read()))

def processthefiles(basefolder, apiConnectionToUse):
    # The files should be structured as such:
    # - MainFolder
    # |--Files 
    # |--| This folder contains all of the files that are to be uploaded
    # |-Account.csv - the Account file from salesforce
    # |-Attachment.csv - this file is from salesforces export, too.
    # |-companyexport.csv - this is the full export of all fields from Infusionsoft
    """This method will be the main logic operator
    thing.  
    """
    with open(os.path.join(basefolder, attachmentExportFileName), 'rb') as infile:
        thisreader = csv.DictReader(infile)
        for eachrow in thisreader:
            currentFilename=eachrow['Id']
            realfilename=eachrow['Name']
            currentAccount = eachrow['AccountId']
            if currentAccount not in sfids.keys():
                # Basically, if it has not been mapped yet, we are going
                # to map it. Then, after everything else is done, we will
                # reference the value through the key.
                sfids[currentAccount] = matchsfAccountIdtocontactid(eachrow['AccountId'], basefolder, apiConnectionToUse)
            attachfile(os.path.join(basefolder, "Files", currentFilename), realfilename, sfids[currentAccount], apiConnectionToUse)


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
                flash(message)
            if not thisconnection.verifyconnection():
                flash("There is a problem with the appname and API key. Please fix them.")
            # This is 2 - ensure that the files needed exist where they should be.
            processthefiles(session['csvfolder'], thisconnection)

    return render_template('allonepage.html', form=form, app = session["app"], apikey = session["apikey"], csvfolder = session["csvfolder"], filesfolder = session["filesfolder"], companyexport = session["companyexport"], contactexport = session["contactexport"])

