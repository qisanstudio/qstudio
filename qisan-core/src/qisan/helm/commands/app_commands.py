# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function


import os
import sys
import json
import importlib

from sh import pip
from flask import Flask
from termcolor import colored
from qisan.platform import config


from ..base import manager

VASSALS = config.common['UWSGI_EMPEROR']
app_manager = manager.subcommand('app')


def get_app_conf(appname):
    #sqlalchemy_gc()
    try:
        module = importlib.import_module(appname)
    except ImportError:
        print(colored('Can\'t import app %s.' % appname,
                      'yellow', attrs=['bold']),
              file=sys.stderr)
        return None

    for name in dir(module):
        app = getattr(module, name)
        if isinstance(app, Flask):  # a flask app
            return app.config
    else:
        print(colored('Can\'t find app %s\'s entry' % appname,
                      'yellow', attrs=['bold']),
              file=sys.stderr)
        return None


def get_vassal_conf(appname):
    with open(os.path.join(VASSALS, appname + '.json'), 'rb') as fp:
        return json.load(fp)


def _iter_installed(with_version=False):
    for line in pip.list():
        pkgname, version = line.strip().split()
        if not pkgname.startswith('qsapp-'):
            continue
        appname = pkgname[6:].replace('-', '_')
        if with_version:
            yield appname, version
        else:
            yield appname


def _iter_registered():
    try:
        vassals = os.listdir(VASSALS)
    except OSError:
        vassals = []

    for vassal in vassals:
        if not vassal.endswith('.json'):
            continue
        yield vassal[:-5]


def _register(*apps):
    try:
        os.makedirs(VASSALS)
    except OSError:
        pass
    if not apps:
        print(colored('No app specified.',
                      'red', attrs=['bold']),
              file=sys.stderr)
        exit(1)
    for appname in apps:
        app_cfg = get_app_conf(appname)
        if app_cfg is None:
            continue
        uwsgi_cfg = {}
        for key in app_cfg:
            if not key.startswith('UWSGI_'):
                continue
            cvtkey = key[6:].lower().replace('_', '-')
            uwsgi_cfg[cvtkey] = app_cfg[key]
        uwsgi_cfg.setdefault('env', []).extend([
            'QISAN_ENVIRON=%s' % config.common['ENVIRON'],
            'QISAN_APPNAME=%s' % appname])
        print('Registering app %s:' % appname, end=' ')
        with open(os.path.join(VASSALS,
                               '%s.json' % appname), 'wb') as fp:
            json.dump({'uwsgi': uwsgi_cfg}, fp)
        print(colored('ok', 'green', attrs=['bold']) + '.')


def list_():
    """枚举所有已经安装的 apps

    """
    registered = {}
    conflict = {}
    for appname in _iter_registered():
        socket = get_vassal_conf(appname)['uwsgi']['socket']
        conflict.setdefault(socket, []).append(appname)
        registered[appname] = socket

    for appname, version in _iter_installed(True):
        # 是否已安装
        print(colored('I', attrs=['bold']), end='')

        # 是否在 uwsgi vassals 中注册
        if appname in registered:
            print(colored('R', attrs=['bold']), end='')
            socket = registered[appname]
            if len(conflict[socket]) > 1:
                # 是否有 socket 冲突
                print(colored('C', 'red', attrs=['bold']), end='')
            else:
                print(' ', end='')
            print('', appname, version, '(' + socket + ')')
        else:
            print('  ', appname, version)

list_.__name__ = b'list'
app_manager.command(list_)


@app_manager.command
def add(*apps):
    """[-apps APP1 APP2 APP3]

    将多个 apps 注册到 uwsgi vassals 中

    参数 -apps 为空时, 枚举所有已经安装的 app (以gkapp-开头)

    """
    if not apps:
        apps = list(_iter_installed())
        for appname in _iter_registered():
            apps.remove(appname)
    if not apps:
        print(colored('All apps are registered.', 'yellow', attrs=['bold']))
        exit(0)
    _register(*apps)
    list_()
