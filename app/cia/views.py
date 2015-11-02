from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User
# from ..email import send_email
from . import main
from .forms import AppApiForm, GetCompCSV, SelectCompCSV

import Tkinter as tk
import tkFileDialog
tk.Tk().withdraw()


def getFilePath(titletext="Please select a file"):
    return tkFileDialog.askopenfilename(title=titletext)

def getFolderPath(titletext="Please select a folder"):
    return tkFileDialog.askdirectory(title=titletext)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = AppApiForm()
    if form.appname.data:
        print "A"
        session['appname'] = form.appname.data
        session['apikey'] = form.api_key.data
        return redirect(url_for('.getCompanies'))
    return render_template('index.html',
                           form=form, appname=session.get('appname'),
                           known=session.get('known', False))

@main.route('/howtogetcomps', methods=['GET', 'POST'])
def getCompanies():
    form = GetCompCSV()
    if form.is_submitted():
        print dir(form)
        print form.submit.data
        session['compcsv'] = getFilePath()
        return redirect(url_for('.selectCompanies')) #This is just a place holder for now
    print dir(form)
    print form.submit.data
    return render_template('getcomps.html', form=form)


@main.route('/getcomps', methods=['GET', 'POST'])
def selectCompanies():
    poop = getFilePath()
    form = SelectCompCSV()
    if form.is_submitted():
        return redirect(url_for('.getRelationshipsFile'))
    return render_template('comps2.html', thisfile=session.get('compcsv'), form=form)

@main.route('/getrels', methods=['GET', 'POST'])
def getRelationshipsFile():
    form=GetCompCSV()
    if form.is_submitted():
        return redirect(url_for('.index')) #This is just a place holder for now
    return render_template('base.html', form=form)
