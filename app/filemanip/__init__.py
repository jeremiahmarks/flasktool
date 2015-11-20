from flask import Blueprint

csvBP = Blueprint('filemanip', __name__)

from . import views, errors
