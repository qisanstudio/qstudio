# -*- coding: utf-8 -*-

from qisan.platform.flask import Blueprint

blueprint_apis = Blueprint('apis', __name__)
blueprint_www = Blueprint('views', __name__)
blueprint_panel = Blueprint('panel', __name__)
