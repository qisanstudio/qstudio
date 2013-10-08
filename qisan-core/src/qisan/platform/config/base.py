# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
配置管理

"""
import os
import imp
from warnings import warn

__all__ = ['BaseConfig', 'LocalFileConfig',
           'YAMLFileConfig', 'PyFileConfig']


class BaseConfig(object):

    def __init__(self, environ=None):

        if not environ:
            if 'QISAN_ENVIRON' in os.environ:
                environ = os.environ['QISAN_ENVIRON']
            else:
                warn(RuntimeWarning(
                    'Environment variable QISAN_ENVIRON is not provided, '
                    'use DEVELOPMENT by default.'))
                environ = 'DEVELOPMENT'
        assert \
            environ in ('DEVELOPMENT', 'STAGING', 'PRODUCTION'), \
            'Illegal environment string: %s' % repr(environ)

        self.environ = environ

    def resolve_inherit(self, rawdict):
        """递归解决配置的继承关系"""
        if '__inherit__' not in rawdict:
            return rawdict  # 没有父层存在, 跳出
        inherit = rawdict.pop('__inherit__')
        assert \
            inherit in ('DEVELOPMENT', 'STAGING', 'PRODUCTION'), \
            'Illegal inherit string: %s' % repr(inherit)
        parent = self.load_default(inherit)
        parent.update(rawdict)
        return parent

    def load_default(self, environ):
        """在此定义读取默认配置的方法

        注意在子类定义时, 返回值要使用 resolve_inherit 处理

        param environ: 工作环境, DEVELOPMENT, STAGING, PRODUCTION 任一

        """
        raise NotImplementedError

    def load_local(self):
        """在此定义读取本地配置的方法

        注意在子类定义时, 返回值要使用 resolve_inherit 处理

        """
        raise NotImplementedError

    def read(self, wrapper=None):
        """读取配置

        param wrapper: 函数, 可对配置的返回值 (默认为 dict) 进行包装,
                       不指定则返回 dict 对象

        """
        rawdict = self.load_local()
        # 去掉非大写的配置
        rawdict = {k: v for k, v in rawdict.iteritems() if k.isupper()}
        for key in dir(self):
            if key.startswith('read_'):
                rawdict = getattr(self, key)(rawdict)
        return wrapper(rawdict) if wrapper else rawdict

    def as_class(self):
        """读取配置, 并转换为一个普通的 class (命名为 _ConfigObject)"""

        def wrapper(rawdict):
            return type(b'_ConfigObject', (object, ), rawdict)

        return self.read(wrapper)

    def __call__(self, wrapper=None):
        """self.read 的捷径"""
        return self.read(wrapper)


class LocalFileConfig(BaseConfig):

    config_default_dir = None
    config_default_files = {
        'DEVELOPMENT': 'development',
        'STAGING': 'staging',
        'PRODUCTION': 'production'}
    config_local_dir = None
    config_local_file = 'local'
    config_suffix = None

    def load_default(self, environ):
        if self.config_default_dir is None or \
           self.config_suffix is None:
            raise NotImplementedError
        path = os.path.join(self.config_default_dir,
                            self.config_default_files[environ] +
                            self.config_suffix)
        rawdict = self.load_file(path).copy()
        if rawdict.get('__inherit__') == environ:
            raise RuntimeError('Inheritance cycle detected in %s, '
                               '__inherit__ equaled %s.' %
                               (path, repr(environ)))
        return self.resolve_inherit(rawdict)

    def load_local(self):
        if self.config_local_dir is None or \
           self.config_suffix is None:
            raise NotImplementedError
        path = os.path.join(self.config_local_dir,
                            self.config_local_file +
                            self.config_suffix)
        if os.path.isfile(path):
            return self.resolve_inherit(self.load_file(path).copy())
        elif os.path.exists(path):
            raise IOError('%s is not a regular file' % path)
        else:
            if self.environ != 'PRODUCTION':
                # 在非生产环境中 load 一次生产环境的配置,
                # 确保其工作正常.
                self.load_default('PRODUCTION')
            return self.load_default(self.environ)

    def load_file(self, path):
        """从文件中读取配置

        继承类中此方法实现具体的读取步骤

        param path: 文件路径

        """
        raise NotImplementedError


class YAMLFileConfig(LocalFileConfig):

    config_suffix = '.yaml'

    def load_file(self, path):
        import yaml
        with open(path, 'rb') as fp:
            return yaml.load(fp.read())


class PyFileConfig(LocalFileConfig):

    config_suffix = '.pycfg'

    def load_file(self, path):
        # copy from Flask.config
        d = imp.new_module('config')
        d.__file__ = path
        try:
            execfile(path, d.__dict__)
        except IOError, e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        rawdict = {}
        for key in dir(d):
            rawdict[key] = getattr(d, key)
        return rawdict


class OSEnvironMixin(object):
    """使用此Mixin后, 可以从环境变量中读取配置"""

    environ_prefix = None

    def read_from_environ(self, rawdict):
        prefix = self.environ_prefix
        if prefix is None:
            return rawdict
        for key in os.environ:
            if not key.startswith(prefix):
                continue
            confkey = key[len(prefix):]
            if not confkey.isupper():
                continue
            rawdict[confkey] = os.environ[key]
        return rawdict
