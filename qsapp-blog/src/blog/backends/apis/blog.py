# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from flask import (Flask, views, render_template, 
                   current_app as app)

#from ..models import BlogModel
from blog.blueprints import blueprint_apis


class BlogAPI(RESTfulOpenAPI):

    def get(self):
        return render_template('blog/list.html')


blueprint_www.add_url_rule(
    '/list', view_func=BlogListView.as_view(b'list'),
    methods=['GET'])

#blueprint_www.before_request(auto_signin(lambda: None))


