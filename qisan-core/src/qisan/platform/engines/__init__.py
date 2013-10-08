#! -*- coding: utf-8 -*-
"""
    所有服务的连接缓存模块
    ~~~~~~~~~~~~~~~~~~~~~~~~

    控制所有的服务连接, 包括:

    * backend
    * redis
    * memcache (XXX: 即将废弃)
    * beanstalk
    * gcache (XXX: 未实现)

    Attributes:
        backend: 后端连接池
        redis_master: Redis 主库连接池
        redis_slave: Redis 从库连接池
        memcache: Memcache 连接
        beanstalk: Beanstalk 队列服务
"""

__author__ = 'Philip Tzou <philip.npc@gmail.com>'

import sys
import types

from flask.helpers import locked_cached_property

from qisan.platform import config


class EnginesModule(types.ModuleType):
    """ hack 模块的载入, 确保各个服务连接可以通过属性加载 """

    @locked_cached_property
    def redis(self):
        from flask.ext.redis import Redis
        return Redis()

    @locked_cached_property
    def db(self):
        from werkzeug.local import LocalProxy
        from qisan.platform.sqlalchemy import SQLAlchemy

        def _find_db():
            from flask import current_app
            if current_app:
                if 'sqlalchemy' in current_app.extensions:
                    return current_app.extensions['sqlalchemy'].db
                else:
                    return SQLAlchemy(current_app)
            else:
                raise RuntimeError('working outside of application context')

        return LocalProxy(_find_db)

    @locked_cached_property
    def mail(self):
        from flask.ext.mail import Mail
        return Mail()

    @locked_cached_property
    def shared_redis(self):
        """应用间共享的redis

        """
        import redis
        url = config.common['SHARED_REDIS']

        return redis.StrictRedis.from_url(url)

old_module = sys.modules[__name__]  # 保持引用计数
new_module = sys.modules[__name__] = EnginesModule(__name__, __doc__)
new_module.__dict__.update({
    '__file__': __file__,
    '__path__': __path__,
    '__author__': __author__,
    '__builtins__': __builtins__,
})

