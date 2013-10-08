# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from flask import (Flask, views, request, render_template, 
                   current_app as app)

#from ..models import BlogModel
from blog.blueprints import blueprint_www


class BlogListView(views.MethodView):

    def get(self):
        app.config['EVERNOTE_CONSUMER_KEY']
        app.config['EVERNOTE_CONSUMER_SECRET']
        print app.config['SERVER_NAME']
        print request.host
        bp = app.blueprints
        print bp['views'].subdomain
        print bp['apis'].subdomain
        print dir(bp['views'])
        return render_template('blog/list.html')


blueprint_www.add_url_rule(
    '/list', view_func=BlogListView.as_view(b'list'),
    methods=['GET'])

#blueprint_www.before_request(auto_signin(lambda: None))

