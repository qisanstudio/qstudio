# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
编码转换模块

"""
import urllib

def smart_str(obj, encoding='U8'):
    if isinstance(obj, unicode):
        obj = obj.encode(encoding)
    else:
        obj = str(obj)
    return obj

def smart_unicode(obj, encoding='U8'):
    if isinstance(obj, unicode):
        pass
    elif isinstance(obj, str):
        obj = unicode(obj, encoding)
    elif hasattr(obj, '__unicode__'):
        obj = obj.__unicode__()
    else:
        obj = unicode(str(obj), encoding)
    return obj

def smart_urlencode(params):
    """
    能够处理 unicode 类型的 urlencode

    """
    if hasattr(params, 'iteritems'):
        params = params.iteritems()
    elif hasattr(params, 'items'):
        params = params.items()
    params = [tuple(map(smart_str, kv)) for kv in params]
    return urllib.urlencode(sorted(params))

def smart_quote(text):
    """
    能够处理 unicode 类型的 quote

    """
    return urllib.quote(smart_str(text))

def quote_like(text):
    '''
    quote special character in sql like condition
    %==>\%
    _==>\_
    \==>\\
    '''
    if not text: return text
    return text.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

def shrink(title, word=25, dot='。。。'):
    '''
    压缩标题，太长的标题给加省略号
    '''
    if len(title) <= word:
        return title
    return title[:word] + dot

