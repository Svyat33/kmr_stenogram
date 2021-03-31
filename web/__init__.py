import asyncio
import http.server
import logging
import logging.config
import os

import aiohttp_jinja2
import aioredis
import jinja2
from aiohttp import web
from dotenv import load_dotenv

from . import base
from .route import configure_handlers, routes

logger = logging.getLogger(__name__)
load_dotenv(os.path.dirname(os.path.abspath(__file__)) + "/.env")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Handler = http.server.SimpleHTTPRequestHandler


async def connect_redis(app):
    app['redis'] = await aioredis.create_redis_pool(
        os.environ.get("REDIS_URL"))


async def disconnect_redis(app):
    app['redis'].close()
    await app['redis'].wait_closed()


async def build_app(loop=None):
    logging.config.dictConfig(base.logging)
    loop = loop or asyncio.get_event_loop()
    loop.set_debug(False)
    middlewares = [

    ]
    application = web.Application(
        middlewares=middlewares
    )
    # connect to redis

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
    application.on_startup.append(connect_redis)
    application.on_cleanup.append(disconnect_redis)
    return application
