# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
    qisan.platform.flask.app
    ~~~~~~~~~~~~~~~~~~~~~~~~

    继承 Flask 实例, 生成 for qisan 的 Flask 实例

"""
import os
import time
import gevent

from flask import Flask, g, request
from flask.helpers import locked_cached_property
from jinja2 import FileSystemLoader

from qisan.platform import config
from .config import init_app_config
from .errors import HTTPException, NotFound, InternalServerError


class QisanFlask(Flask):
    
    def __init__(self, *args, **kwargs):
        """
        初始化 Flask 实例

        这里主要绑定了 flask-sqlalchemy 的数据库连接

        """
        super(QisanFlask, self).__init__(*args, **kwargs)
        init_app_config(self)

        # 全局 url_for
        #self.url_build_error_handlers.append(self._external_url_handler)

        @self.before_request
        def add_x_start():
            g.__x_start = time.time()

        @self.after_request
        def add_x_headers(response):
            try:
                duration = time.time() - g.__x_start
            except AttributeError:
                duration = -0.0001
            response.headers.add(
                b'X-Served-By',
                request.environ.get('uwsgi.node', b'Unknown') or b'Error')
            response.headers.add(b'X-Served-In-Seconds', b'%.4f' % duration)
            return response

        # 开发模式下启用调试器
        self.debugger_wsgi_app = None
        if config.common['ENVIRON'] == 'DEVELOPMENT' and self.debug:
            # 如果是uwsgi且为单进程模式, 则启用控制台调试器
            try:
                import uwsgi
                evalex = uwsgi.numproc == 1
            except ImportError:
                evalex = True
            from werkzeug.debug import DebuggedApplication
            self.debugger_wsgi_app = DebuggedApplication(self.wsgi_app, evalex)

            # 记录 greenlet 的 id
            @self.after_request
            def add_greenlet_headers(response):
                ident = id(gevent.getcurrent())
                response.headers.add(b'X-Greenlet-Ident', ident)
                return response

        # 绑定默认的 404 和 500 错误处理
        @self.errorhandler(404)
        def page_not_found(error):
            if isinstance(error, HTTPException):
                return error
            else:
                return NotFound('找不到网页')

        @self.errorhandler(500)
        def internal_server_error(error):
            if isinstance(error, HTTPException):
                return error
            else:
                return InternalServerError('服务器正在维护，请稍后访问')
    
    @property
    def external_url_adapter(self):
        from qisan.platform.routing_rules import url_map as external_url_map
        if request:
            return external_url_map.bind_to_environ(
                request.environ,
                server_name=self.server_name_with_port(request.environ))
        else:
            server_name = self.config.get('SERVER_NAME')
            return external_url_map.bind(
                server_name,
                script_name=self.config['APPLICATION_ROOT'] or '/',
                url_scheme=self.config['PREFERRED_URL_SCHEME'])


    def _external_url_handler(self, error, endpoint, values):
        """在本地的 url_for 无法生成链接时, 查找全局路由表"""
        method = values.pop('_method', None)
        anchor = values.pop('_anchor', None)
        values.pop('_external', None)
        ext_adapter = self.external_url_adapter
        if config.common['ENVIRON'] == 'PRODUCTION':
            # 生产环境中, auth 应用使用 https
            if endpoint[:5] == 'auth:':
                ext_adapter.url_scheme = 'https'
            else:
                ext_adapter.url_scheme = 'http'
        rv = ext_adapter.build(endpoint, values, method=method,
                               force_external=True)
        if anchor is not None:
            rv += '#' + url_quote(anchor)
        return rv


    @locked_cached_property
    def jinja_loader(self):
        """The Jinja loader for this package bound object.

        .. versionadded:: 0.5
        """
        if self.template_folder is not None:
            return FileSystemLoader([
                os.path.join(self.root_path, 'frontends', self.template_folder),
                os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             'templates')])    


    def __call__(self, environ, start_response):
        wsgi_app = self.wsgi_app
        return wsgi_app(environ, start_response)
