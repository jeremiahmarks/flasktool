from flask import render_template, session, redirect, url_for, current_app, request, flash
# from ..email import send_email
from . import csvBP as main

from .. import ISServer
from .. import fileprocessor
from .. import commonFunctions as funcs

from flask.ext.wtf import Form
from wtforms import SubmitField, StringField

import os
import sys
import csv
import glob
import datetime
import base64
import pickle

class csvColumnNames(Form):
  @classmethod
  def addColumn(cls, name, field):
    print "yay!"
    setattr(cls, name, field)
  submit = SubmitField('Submit')




@main.route('/files', methods=['GET', 'POST'])
def start():
    # return redirect(url_for('csv_blueprint.index'))
    testcols=['a', 'b', 'c']
    neededdata=['file1', 'file2']
    newForm = csvColumnNames()
    for eachcol in testcols:
        newForm.addColumn(eachcol, StringField())
    return render_template('index2.html', form=newForm, cols=testcols)
