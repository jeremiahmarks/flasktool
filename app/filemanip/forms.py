from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import Required


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class AppApiForm(Form):
    appname = StringField("Appname", validators=[Required()])
    api_key = StringField("Api Key", validators=[Required()])
    submit = SubmitField("Next")

class GetCompCSV(Form):
    thisfile = FileField("compCSV")
    submit = SubmitField("selectFile")

class SelectCompCSV(Form):
    submit = SubmitField("NextStep")

class MainForm(Form):
  """Things that need to be included in this form:
    * appname
    * apikey
    * pathtocsv folder (for ACCOUNT.csv and ATTACHMENT.csv)
    * path to files folder (basically the folder where the files are)
    * path to company export
    * path to contact export
  """
<<<<<<< HEAD
=======
  # setapp = SubmitField("SetApp")
  # setapikey = SubmitField('SetAPIKey')
  # setcsvfolder = SubmitField("SetCsvFolder")
  # setfilesfolder = SubmitField("SetFilesFolder")
  # setcompanyexport = SubmitField("SetCompanyExport")
  # setcontactexport = SubmitField('SetContactExport')

>>>>>>> origin/addmenu
  app = StringField("app")
  apikey = StringField("apikey")
  accountCSV = StringField("accountCSV")
  attachmentCSV = StringField("attachmentCSV")
  companyexport = StringField("companyexport")
  filesfolder = StringField("filesfolder")

<<<<<<< HEAD
class FileForm(Form):
  file1 = StringField("file1")
  file2 = StringField("file2")
=======

>>>>>>> origin/addmenu
