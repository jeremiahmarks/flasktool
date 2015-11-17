from flask import Blueprint

main = Blueprint('filemanip', __name__)

from . import views, errors
