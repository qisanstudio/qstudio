# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

import os
from os import path
import setuptools


try:
    # work-around to avoid "setup.py test" error
    # see: http://bugs.python.org/issue15881#msg170215
    import multiprocessing
    assert multiprocessing
except ImportError:
    pass


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def reqs(filename):
    with open(path.join(os.getcwd(),
                        'requirements',
                        filename)) as fp:
        return filter(None, [strip_comments(l)
                             for l in fp.readlines()])


package_name = path.basename(os.getcwd())


setup_params = dict(
    name=package_name,
    version="0.1",
    url="http://wiki.yimiqisan.com/",
    author="yimiqisan",
    author_email="yimiqisan@gmail.com",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
#    package_data = {
#        'blog': ['frontends/templates/blog/*.html'],
#    },
    zip_safe=False,
#    dependency_links=['http://pypi.iguokr.com'],
    install_requires=reqs('requirements.txt'))

if __name__ == '__main__':
    setuptools.setup(**setup_params)
