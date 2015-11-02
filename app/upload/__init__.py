from flask import Blueprint

main = Blueprint('upload', __name__)

from . import views, errors
