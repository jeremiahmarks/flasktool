from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User
# from ..email import send_email
from . import main
from .forms import AppApiForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = AppApiForm()
    if form.appname.data:
        session['appname'] = form.appname.data
        session['apikey'] = form.api_key.data
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, appname=session.get('appname'),
                           known=session.get('known', False))
