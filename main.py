import os

from aiohttp import web
from dotenv import load_dotenv

from web import build_app
load_dotenv(".env")
if __name__ == '__main__':
    web.run_app(build_app(), port=os.getenv('PORT', '8000'))