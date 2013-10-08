#! /usr/bin/env python
# -*- coding: utf-8 -*-


from qisan.platform.flask import QisanFlask


app = QisanFlask(__name__)

with app.app_context():
    from .backends import apis
    from .backends import views
    from .backends import panel
    from .blueprints import (blueprint_apis, 
                             blueprint_www,
                             blueprint_panel)

    app.register_blueprint(blueprint_apis,
                           url_prefix='/blog', subdomain='apis')
    app.register_blueprint(blueprint_www,
                           url_prefix='/blog', subdomain='www')
    app.register_blueprint(blueprint_panel,
                           url_prefix='/blog', subdomain='panel')


