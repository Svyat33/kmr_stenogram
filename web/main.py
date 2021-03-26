import asyncio
import http.server
import logging
import logging.config
import os

import aiohttp_jinja2
import jinja2
import redis
from aiohttp import web

from config import base
from route import configure_handlers, routes

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.getenv('PORT', '8000'))
Handler = http.server.SimpleHTTPRequestHandler
r = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/1/"))
my_redis = r.client()


def build_app(loop=None):
    logging.config.dictConfig(base.logging)
    loop = loop or asyncio.get_event_loop()
    loop.set_debug(False)
    middlewares = [

    ]
    application = web.Application(
        middlewares=middlewares
    )
    # static files

    application.router.add_static('/static',
                                  os.path.join(BASE_DIR, '../static'))
    # templates
    template_dir = os.path.join(os.path.dirname(__file__), '../templates')
    aiohttp_jinja2.setup(
        application, loader=jinja2.FileSystemLoader(template_dir)
    )
    # connect routes
    configure_handlers(application, routes)

    # shutdown connection clean-up
    async def on_shutdown_close_conns(app):
        if app.connections:
            logger.info('Force closing %s open stream connections.',
                        len(app.connections))
            for resp in app.connections:
                resp.should_stop = True

    application.connections = set()
    application.on_shutdown.append(on_shutdown_close_conns)

    return application


if __name__ == '__main__':
    main = build_app()
    web.run_app(main)
