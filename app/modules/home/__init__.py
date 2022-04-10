from flask import Blueprint

home_blu = Blueprint("home", __name__)

# from app.modules.home.views import *

from . import routes, events