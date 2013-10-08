#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import os
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
    with open(os.path.join(os.getcwd(),
                           'requirements',
                           filename)) as fp:
        return filter(None, [strip_comments(l)
                             for l in fp.readlines()])

setup_params = dict(
    name="qisan-core",
    version='1.0',
    url="http://wiki.yimiqisan.com/",
    author="yimiqisan",
    author_email="yimiqisan@gmail.com",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=reqs('requirements.txt'),
    namespace_packages=['qisan'],
    entry_points={
        'console_scripts': [
            'helm = qisan.helm:main',
        ],
    })

if __name__ == '__main__':
    setuptools.setup(**setup_params)
