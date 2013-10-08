#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import glob
import inspect
from collections import OrderedDict
from multiprocessing import Process, Queue

from werkzeug.routing import Rule
from guokr.platform import config

base = os.environ['BASE']


def get_all_confs():
    confs = glob.glob(os.path.join(base, 'guokr/apps/*/app.yaml'))
    confs.extend(glob.glob(os.path.join(base, 'guokr/services/*/app.yaml')))
    return sorted(confs)


def get_app_rules(apppath, module, rules):
    sys.path.insert(0, apppath)
    mod = __import__(module[0])
    url_map = getattr(mod, module[1]).url_map
    args = inspect.getargspec(Rule.__init__).args
    args.remove('self')
    result = []
    for rule in url_map.iter_rules():
        kvs = OrderedDict()
        for arg in args:
            if arg == 'string':
                _arg = 'rule'
            else:
                _arg = arg
            val = getattr(rule, _arg)
            kvs[arg] = val
        result.append(kvs)
    rules.put(result)


def get_all_rules():
    global_conf = config.load_yaml(os.path.join(base, 'guokr.yaml'))
    confs = get_all_confs()
    ret = OrderedDict()
    for confpath in confs:
        try:
            appconf = config.load_yaml(confpath)
        except TypeError:
            continue
        appname = appconf['APPNAME']
        conf = global_conf['APP_' + appname.upper()]
        conf.update(appconf)
        module = conf.get('MODULE', 'app:app').split(':')
        apppath = os.path.dirname(confpath)
        rules = Queue()
        p = Process(target=get_app_rules, args=(apppath, module, rules))
        p.start()
        ret[appname] = (p, rules)
    for appname, (p, rules) in ret.iteritems():
        p.join()
        ret[appname] = rules.get()
    return ret


def dump_rules(appname, rules):
    ret = []
    for rule in rules:
        if rule['endpoint'] in ('static', 'sslstatic'):
            continue
        rule['endpoint'] = appname + ':' + rule['endpoint']
        args = []
        for k, v in rule.iteritems():
            if k != 'string':
                if k in ('build_only', 'alias'):
                    if v is False:
                        continue
                elif v is None:
                    continue
                arg = '%s=%s' % (k, repr(v))
            else:
                arg = repr(v)
            args.append(arg)
        text = 'Rule(' + ', '.join(args) + ')'
        ret.append(text)
    if ret:
        return '    ' + ',\n    '.join(ret) + ','
    else:
        return ''


def main(fp):
    app_rules = get_all_rules()

    print >> fp, '# -*- coding: utf-8 -*-'
    print >> fp, '"""Generated routing rules by tools/make_routing_rules.py'
    print >> fp, ''
    print >> fp, '@generated'
    print >> fp, ''
    print >> fp, '"""'
    print >> fp, '# flake8: noqa'
    print >> fp, '# hghooks: no-pep8'
    print >> fp, ''
    print >> fp, 'from werkzeug.routing import Map, Rule'
    print >> fp, ''
    print >> fp, 'from guokr.platform.flask import addition_converters'
    print >> fp, ''
    print >> fp, 'url_map = Map(['
    print >> fp, ''
    for appname, rules in app_rules.iteritems():
        print >> fp, '### START OF RULES SET %s ###' % appname
        print >> fp, ''
        print >> fp, dump_rules(appname, rules)
        print >> fp, ''
        print >> fp, '### END OF RULES SET %s ###' % appname
        print >> fp, ''

    print >> fp, "    Rule('/<path:filename>', endpoint=':static:', subdomain='static', methods=['GET'], strict_slashes=True),"  # NOPEP8
    print >> fp, "    Rule('/<path:filename>', endpoint=':static:ssl', subdomain='sslstatic', methods=['GET'], strict_slashes=True),"  # NOPEP8
    print >> fp, "    Rule('/special/<regex(\".*\"):filename>', endpoint=':special:', subdomain='www', methods=['GET'], strict_slashes=True),"  # NOPEP8
    print >> fp, "    Rule('/recommend/<regex(\"(group|tag|question|userprofile)/(group|tag|answer|by_group|by_tag|by_question|by_user)\"):action>', endpoint='galahad:', subdomain='algo', methods=['GET', 'POST', 'PUT', 'DELETE']),"  # NOPEP8
    print >> fp, "    Rule('/recommend/<regex(\"(question|article)/by_topic\"):action>', endpoint='lancelot:', subdomain='algo', methods=['GET', 'POST', 'PUT', 'DELETE']),"  # NOPEP8
    print >> fp, "    Rule('/recommend/<regex(\"(group|tag|question)/(by_group|by_tag|by_question|by_user)\"):action>', endpoint='galahad:', subdomain='apis', methods=['GET']),"  # NOPEP8
    print >> fp, "    Rule('/recommend/<regex(\"(question|article)/by_topic\"):action>', endpoint='lancelot:', subdomain='apis', methods=['GET']),"  # NOPEP8
    print >> fp, "    Rule('/appraiser/<path:path_info>', endpoint='bedivere:', subdomain='algo', methods=['GET', 'POST', 'PUT', 'DELETE']),"  # NOPEP8
    print >> fp, "    Rule('/tpksim/<path:path_info>', endpoint='lancelot:', subdomain='algo', methods=['GET', 'POST', 'PUT', 'DELETE']),"  # NOPEP8
    print >> fp, ''
    print >> fp, '], converters=addition_converters)'

if __name__ == '__main__':
    print 'Making routing rules ...'
    fname = sys.argv[1]
    with open(fname + '.new', 'wb') as fp:
        main(fp)
    os.rename(fname + '.new', fname)
