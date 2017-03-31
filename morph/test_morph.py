# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/30
@description: 
"""

import os
import sys
import traceback
import tornado.web
import tornado.httpserver
from tornado import ioloop
from tornado import options
from morph.config import settings
from morph.lib.utils.logger_util import logger


SETTINGS = dict(
    template_path=os.path.join(os.path.dirname(sys.argv[0]), "templates"),
    static_path=os.path.join(os.path.dirname(sys.argv[0]), "static"),
    cookie_secret="_furion_security_session_secret_wavGQTsY&I7BQouiKaY!EqCeKuRlL8TY",
    login_url="/",
)


session_settings = dict(
    driver="redis",
    driver_settings=dict(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        max_connections=settings.redis_max_connections
    ),
    cookie_config=dict(
        domain=".actneed.com",
        expires_days=30,
    )
)

handlers = [
]


options.define('port', default=8800, type=int)


def main():
    try:
        options.parse_command_line()
        port = options.options.port
        settings.configure('PORT', port)

        app = tornado.web.Application(
            handlers=handlers,
            session=session_settings,
            **SETTINGS
        )
        server = tornado.httpserver.HTTPServer(app)
        server.listen(settings.port)
        ioloop.IOLoop().instance().start()

    except Exception, e:
        print traceback.format_exc(e)
        logger.error(traceback.format_exc(e))


if __name__ == '__main__':
    print "the server is going to start..."
    main()