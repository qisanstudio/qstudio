# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from qisan.platform import config

from ..base import manager
from ..utils import CommandHook

from . import uwsgi_commands, app_commands #nginx_commands, app_commands

CommandHook('common.before_start')
CommandHook('common.before_stop')
CommandHook('common.before_restart')
CommandHook('common.before_reload')
CommandHook('common.before_touch')


def is_prod():
    return config.common['ENVIRON'] == 'PRODUCTION'


def _nginx_start():
    if not is_prod():
        nginx_commands.restart()


def _nginx_stop():
    if not is_prod():
        nginx_commands.stop()


def _nginx_reload():
    if not is_prod():
        nginx_commands.reload()


CommandHook.bind(['common.before_start',
                  'common.before_restart'], _nginx_start)
CommandHook.bind('common.before_stop', _nginx_stop)
CommandHook.bind(['common.before_reload',
                  'common.before_touch'], _nginx_reload)


@manager.command
def start():
    CommandHook.trigger('common.before_start')
    uwsgi_commands.start()


@manager.command
def debug():
    try:
        CommandHook.trigger('common.before_start')
        uwsgi_commands.debug()
    finally:
        CommandHook.trigger('common.before_stop')


@manager.command
def reload():
    CommandHook.trigger('common.before_reload')
    uwsgi_commands.reload()


@manager.command
def stop():
    CommandHook.trigger('common.before_stop')
    uwsgi_commands.stop()


@manager.command
def restart():
    CommandHook.trigger('common.before_restart')
    uwsgi_commands.restart()


@manager.command
def touch(*app):
    CommandHook.trigger('common.before_touch')
    app_commands.touch(*app)
