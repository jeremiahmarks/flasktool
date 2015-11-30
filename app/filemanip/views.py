from flask import render_template, session, redirect, url_for, current_app, request, flash
# from ..email import send_email
from . import csvBP as main
from .forms import FileForm, csvColumnNames
from .. import ISServer
from .. import fileprocessor
from .. import commonFunctions as funcs

from wtforms import SubmitField

import os
import sys
import csv
import glob
import datetime
import base64
import pickle

@main.route('/files', methods=['GET', 'POST'])
def start():
    # return redirect(url_for('csv_blueprint.index'))
    neededdata=['file1', 'file2']
    form = FileForm()
    if form.is_submitted():
        session['file1'] = {}
        session['file1']['path'] = funcs.getFilePath()
        session['file1']['columns'] = list(fileprocessor.CSVFileActions(session['file1']['path']).getcolnames())
        return redirect(url_for('.chooseHeaders'))
    return render_template('vlookup.html', form=form, file1=session['file1'])
    # return render_template('vlookup.html', form=form, file1=session['file1'], file2=session['file2'])

@main.route('/file1', methods=['GET', 'POST'])
def chooseHeaders():
    # This method will provide the screen to choose which
    # the primary lookup column will be.
    form = csvColumnNames()
    if form.is_submitted():
        # here we will need to save the column
        session['file1']['maincol']=form.btn.data
    return render_template('vlookup.html', form=form)

@main.route('/file2', methods=['GET', 'POST'])
def part2():
    pass
