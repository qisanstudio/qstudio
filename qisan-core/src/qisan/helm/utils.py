# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    Code from: http://code.activestate.com/recipes/577058/

    :param question: a string that is presented to the user.
    :param default: the presumed answer if the user just hits <Enter>.
                    It must be "yes" (the default), "no" or None (meaning
                    an answer is required of the user).

    :return: True or False.

    """
    valid = {"yes": True,
             "y": True,
             "ye": True,
             "no": False,
             "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def multiline_input(prompt=''):
    """Multiple lines version of raw_input()

    Empty line, Ctrl-D (^D, Linux) or
    Ctrl-Z (^Z, Windows) will end the input.

    :param prompt: if given, is printed without a trailling newline
                   before reading

    :return: string

    """
    print(prompt)
    inputbuf = ''
    while True:
        try:
            line = raw_input('    ')
        except EOFError:
            break
        if not line.strip():
            break
        inputbuf += line
    return inputbuf


class CommandHook(object):

    __hooks = {}

    def __init__(self, name):
        self._funcs = []
        self.__hooks[name] = self

    @classmethod
    def trigger(self, *hookname):
        for name in hookname:
            self.__hooks[name]()

    @classmethod
    def bind(self, hookname, func):
        if isinstance(hookname, basestring):
            hookname = [hookname]
        for name in hookname:
            self.__hooks[name](func)

    def __call__(self, *funcs):
        if not funcs:
            for func in self._funcs:
                func()
        else:
            self._funcs.extend(funcs)
