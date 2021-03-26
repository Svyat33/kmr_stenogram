import os

from aiohttp import web

from web import build_app, base

if __name__ == '__main__':
    main = build_app(base)
    web.run_app(main, port=os.getenv('PORT', '8000'))