from flask import render_template, session, redirect, url_for, current_app, request
from .. import db
from ..models import User
# from ..email import send_email
from . import main
from .forms import AppApiForm, GetCompCSV, SelectCompCSV, MainForm

import Tkinter as tk
import tkFileDialog
tk.Tk().withdraw()


def getFilePath(titletext="Please select a file"):
    return tkFileDialog.askopenfilename(title=titletext)

def getFolderPath(titletext="Please select a folder"):
    return tkFileDialog.askdirectory(title=titletext)

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
        if request.form["btn"] == "setapp":
            session['app'] = form.app.data
        if request.form["btn"] == "setapikey":
            session['apikey'] = form.apikey.data
        if request.form["btn"] == "setcsvfolder":
            session['csvfolder'] = getFolderPath()
        if request.form["btn"] == "setfilesfolder":
            session['filesfolder'] = getFolderPath()
        if request.form["btn"] == "setcompanyexport":
            session['companyexport'] = getFilePath()
        if request.form["btn"] == "setcontactexport":
            session['contactexport'] = getFilePath()
    return render_template('allonepage.html', form=form, app = session["app"], apikey = session["apikey"], csvfolder = session["csvfolder"], filesfolder = session["filesfolder"], companyexport = session["companyexport"], contactexport = session["contactexport"])

