import asyncio
import logging
import http
import json
from random import randint
from websockets import server
from gateway import handler, connection
from gateway.db import loop
from gateway.vendor import snowflake

logging.basicConfig(level=logging.DEBUG)

ports_ready = asyncio.Event()

async def health_check(path, head):
    if path == '/health':
        return http.HTTPStatus.OK, [], b'OK\n'
    elif path == '/port':
        return http.HTTPStatus.OK, [], '{}'.format(json.dumps({'port': get_port()})).encode()


async def start_gateway():
    print('DEBUG:gateway:Starting Gateway')
    await asyncio.sleep(15)

    for port in range(100):
        try:
            await server.serve(
                    handler.gateway_handler,
                    '0.0.0.0',
                    port,
                    ping_timeout=20,
                    process_request=health_check,
                )
            handler.available[port] = []
            connection.sessions[port] = []
        except:
            pass

    ports_ready.set()

def get_port() -> int:
    # port = randint(1024, 49151)
    port = randint(1, 100)

    av = connection.sessions.get(port)

    if av == None:
        return get_port()

    if len(av) > 50000:
        return get_port()

    return port

loop.run_until_complete(start_gateway())
loop.run_forever()
