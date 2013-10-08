# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from flask import (views, request, render_template,
                   current_app as app)

#from ..models import BlogModel
from blog.blueprints import blueprint_www


class BlogListView(views.MethodView):

    def get(self):
        app.config['EVERNOTE_CONSUMER_KEY']
        app.config['EVERNOTE_CONSUMER_SECRET']
        return render_template('blog/list.html')


blueprint_www.add_url_rule(
    '/list', view_func=BlogListView.as_view(b'list'),
    methods=['GET'])

