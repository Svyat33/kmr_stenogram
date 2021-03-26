import os

from aiohttp import web

from web import build_app

if __name__ == '__main__':
    web.run_app(build_app(), port=os.getenv('PORT', '8000'))