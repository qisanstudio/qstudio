# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys

from sh import uwsgi, kill, ErrorReturnCode
from termcolor import colored
from qisan.platform import config

from ..base import manager


uwsgi_manager = manager.subcommand('uwsgi')


def _uwsgi_common(*args):
    args = list(args)
    for key in config.common:
        if not key.startswith('UWSGI_') or \
           key == 'UWSGI_LOGFILE':  # LOGFILE 为特殊配置
            continue
        val = config.common[key]
        if key.startswith('UWSGI_VASSAL_'):
            continue
        else:
            arg = '--' + key[6:].lower().replace('_', '-')
            if not val is True:
                arg += '=%s' % val
            args.append(arg)
    print(args)
    #uwsgi(*args, _out=sys.stdout)


def is_alive(pidfile):
    if os.path.exists(pidfile):
        with open(pidfile, 'rb') as fp:
            pid = fp.read()
        try:
            kill('-0', pid)
            return True
        except ErrorReturnCode:
            return False
    return False


@uwsgi_manager.command
def start():
    pidfile = config.common['UWSGI_PIDFILE']
    print('Starting uWSGI:', end=' ')
    if is_alive(pidfile):
        print(colored('failed', 'red', attrs=['bold']) +
              ', uWSGI is already running.')
    else:
        _uwsgi_common('--daemonize=' +
                      config.common['UWSGI_LOGFILE'])
        print(colored('uWSGI', 'green', attrs=['bold']) + '.')


@uwsgi_manager.command
def debug():
    pidfile = config.common['UWSGI_PIDFILE']
    print('Debugging uWSGI:', end=' ')
    if is_alive(pidfile):
        print(colored('failed', 'red', attrs=['bold']) +
              ', uWSGI is already running.')
    else:
        _uwsgi_common('--catch-exceptions')
        print(colored('uWSGI', 'green', attrs=['bold']) + '.')


@uwsgi_manager.command
def reload():
    pidfile = config.common['UWSGI_PIDFILE']
    print('Reloading uWSGI:', end=' ')
    try:
        uwsgi('--reload', pidfile)
    except ErrorReturnCode:
        print(colored('failed', 'red', attrs=['bold']) + '.')
    else:
        print(colored('uWSGI', 'green', attrs=['bold']) + '.')


@uwsgi_manager.command
def stop():
    pidfile = config.common['UWSGI_PIDFILE']
    print('Stopping uWSGI:', end=' ')
    try:
        uwsgi('--stop', pidfile)
    except ErrorReturnCode:
        print(colored('failed', 'red', attrs=['bold']) + '.')
    else:
        print(colored('uWSGI', 'green', attrs=['bold']) + '.')


@uwsgi_manager.command
def restart():
    pidfile = config.common['UWSGI_PIDFILE']
    stop()
    count = 0
    while is_alive(pidfile):
        print('.', end='')
        count += 1
    print('\b' * count)
    start()
