import datetime
import os

from aiohttp.web import StreamResponse, HTTPNotAcceptable
import aiohttp_jinja2
import asyncio
import io
import json
import logging
import time

log = logging.getLogger(__name__)


@aiohttp_jinja2.template('index.jinja2')
async def index(request):
    redis = request.app['redis']
    last_run = int(await redis.get('last_work'))
    print(os.getenv('LAST_DOC_KEY'))
    lst = await redis.lrange(os.getenv('LAST_DOC_KEY'),
                             0,
                             int(os.getenv('LAST_DOC_COUNT')))
    ret = []
    for raw_doc in lst:
        ret.append(json.loads(raw_doc.decode()))
    return {
        'last_work': datetime.datetime.fromtimestamp(last_run),
        'last_docs': ret
    }


async def tick(request):
    if 'text/event-stream' not in request.headers.getall('ACCEPT', []):
        raise HTTPNotAcceptable(
            reason="'text/event-stream' not found in Accept headers.")

    resp = StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )

    log.debug('Opening new event stream on request: %s', request)
    await resp.prepare(request)

    request.app.connections.add(resp)
    resp.should_stop = False
    try:
        while not resp.should_stop:
            ts = time.monotonic()
            payload = json.dumps({'data': ts})
            resp.write(build_message(payload, id=ts, event='tick'))
            await resp.drain()
            await asyncio.sleep(1)

    finally:
        request.app.connections.remove(resp)

    return resp


def build_message(data, id=None, event=None):
    buffer = io.BytesIO()
    if id is not None:
        buffer.write('id: {0}\r\n'.format(id).encode('utf-8'))
    if event is not None:
        buffer.write('event: {0}\r\n'.format(event).encode('utf-8'))
    for chunk in data.split('\r\n'):
        buffer.write('data: {0}\r\n'.format(chunk).encode('utf-8'))
    buffer.write(b'\r\n')
    return buffer.getvalue()
