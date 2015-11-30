from flask import Blueprint

csvBP = Blueprint('coolform', __name__)

from . import views, errors
