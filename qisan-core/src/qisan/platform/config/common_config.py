# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
全局配置管理

"""
import os

from .base import PyFileConfig, OSEnvironMixin


class CommonConfig(PyFileConfig, OSEnvironMixin):

    config_default_dir = os.path.join(os.path.dirname(__file__), 'common')
    config_local_dir = os.path.expanduser('~/.qstudio/common')
    environ_prefix = 'QISAN_'

