# -*- coding: utf-8 -*-
"""
OpenAPI 的 Flask 辅助模块

"""
from __future__ import unicode_literals

import json

from flask import request
from flask import render_template
from werkzeug.exceptions import \
    HTTPException as _HTTPException, \
    BadRequest as _BadRequest, \
    Unauthorized as _Unauthorized, \
    Forbidden as _Forbidden, \
    NotFound as _NotFound, \
    InternalServerError as _InternalServerError, \
    MethodNotAllowed as _MethodNotAllowed
from qisan.platform import errors
from qisan.platform.contribs import encoding


class HTTPException(errors.QisanException, _HTTPException):
    """封装原有方法, 实现自定义模板"""

    def get_body(self, environ):
        """Get the HTML body."""
        return render_template('error_page.html', error=self)


class BadRequest(HTTPException, _BadRequest):
    pass


class Unauthorized(HTTPException, _Unauthorized):
    pass


class Forbidden(HTTPException, _Forbidden):
    pass


class NotFound(HTTPException, _NotFound):
    pass


class InternalServerError(HTTPException, _InternalServerError):
    pass


class MethodNotAllowed(HTTPException, _MethodNotAllowed):
    pass


class APIError(HTTPException):
    """
    发起 HTTP Exception 错误

    """
    def __init__(self, error_code, error):
        error = encoding.smart_unicode(error)
        if 'REQUEST_URI' in request.environ:
            request_uri = request.environ['REQUEST_URI']
        else:
            request_uri = request.script_root + request.path
        self.result = {
            'ok': False,
            'error_code': error_code,
            'error': error,
            'request_uri': request_uri,
        }
        super(APIError, self).__init__(description='%s: %s' %
                                       (error_code, error))

    def get_body(self, environ):
        """GET the JSON Body."""
        return json.dumps(self.result)

    def get_header(self, environ):
        """Get a list of headers."""
        return [('Content-Type', 'application/json')]


class APIBadRequest(APIError, BadRequest):
    """400 Bad Request"""
    pass


class APIUnauthorized(APIError, Unauthorized):
    """401 Unauthorized"""
    pass


class APIForbidden(APIError, Forbidden):
    """403 Forbidden"""
    pass


class APINotFound(APIError, NotFound):
    """404 Not Found"""
    pass


class APIInternalServerError(APIError, InternalServerError):
    """500 Internal Server Error"""
    pass


class APIMethodNotAllowed(APIError, MethodNotAllowed):
    """405 Method Not Allowed"""
    pass

