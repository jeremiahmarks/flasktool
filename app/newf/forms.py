from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FileField, SelectField, widgets
from wtforms.validators import Required


class csvColumnNames(Form):
  @classmethod
  def addColumn(cls, name, field):
    print "yay!"
    setattr(cls, name, field)
    # return cls
  submit = SubmitField('Submit')

