from flask import Blueprint

main = Blueprint('cia', __name__)

from . import views, errors
