from aiohttp import web

from config import base
from web.main import build_app

if __name__ == '__main__':
    main = build_app(base)
    web.run_app(main)