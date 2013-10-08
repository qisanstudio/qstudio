# -*- coding: utf-8 -*-

import sys

__ENCODING = None
__GEVENT = None
__JSON = None
__DATETIME = None


def patch_encoding():
    global __ENCODING

    if __ENCODING:
        return

    # hack sys, 使默认编码为UTF-8
    reload(sys)
    sys.setdefaultencoding('UTF-8')
    __ENCODING = True


def patch_gevent():
    global __GEVENT

    if __GEVENT:
        return

    if 'threading' in sys.modules:
        sys.modules.pop('threading')

    import gevent
    import gevent.monkey
    gevent.monkey.patch_all()

    import psycogreen.gevent
    psycogreen.gevent.patch_psycopg()
    __GEVENT = True


def patch_json():
    global __JSON

    if __JSON:
        return

    from qisan.platform.contribs.monkeypatch import mp_json
    mp_json.patch()
    __JSON = True


def patch_datetime():
    global __DATETIME

    if __DATETIME:
        return

    from qisan.platform.contribs.monkeypatch import tz_datetime
    tz_datetime.patch()
    __DATETIME = True


def patch_all():
    patch_encoding()
    patch_gevent()
    patch_json()
    patch_datetime()


patch_all()
