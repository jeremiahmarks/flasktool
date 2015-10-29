from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class AppApiForm(Form):
    appname = StringField("Appname", validators=[Required()])
    api_key = StringField("Api Key", validators=[Required()])
    submit = SubmitField("Next")
