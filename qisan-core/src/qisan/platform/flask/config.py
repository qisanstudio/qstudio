# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from werkzeug import cached_property
from qisan.platform import config


class QisanFlaskConfig(config.PyFileConfig, config.OSEnvironMixin):

    def __init__(self, app, environ=None):

        self.app = app
        super(QisanFlaskConfig, self).__init__(environ)
        with app.app_context():
            app.config.update(self())

    @cached_property
    def config_default_dir(self):
        return os.path.join(self.app.root_path, 'config')

    @cached_property
    def config_local_dir(self):
        return os.path.expanduser('~/.qstudio/qsapp-%s' %
                                  self.app.import_name)

    @cached_property
    def environ_prefix(self):
        return 'QSAPP_' + self.app.import_name.upper() + '_'

    def read_common_config(self, rawdict):
        for key, val in config.common.iteritems():
            if key.startswith('FLASK_'):
                rawdict.setdefault(key[6:], val)
            elif key.startswith('UWSGI_VASSAL_'):
                rawdict.setdefault('UWSGI_' + key[13:], val)
        return rawdict


def init_app_config(app):
    return QisanFlaskConfig(app)

