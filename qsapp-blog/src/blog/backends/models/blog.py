# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from flask import request, url_for

from qisan.platform.engines import db

__all__ = ['BlogModel']

class BlogModel(db.Model):
    __tablename__ = 'blog'

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
