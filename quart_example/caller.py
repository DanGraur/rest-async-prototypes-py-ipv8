import asyncio

import requests
from quart import Quart
from server import AsyncQuartEndpoint, SyncQuartEndpoint

app = Quart(__name__)


async def programatic_calls():

    loop = asyncio.get_event_loop()

    future_1 = loop.run_in_executor(None, requests.get, 'http://localhost:8081/sync/math?a=1&b=3&op=div')
    future_2 = loop.run_in_executor(None, requests.get, 'http://localhost:8081/sync/echo?msg=this%20is%20a%20message.')

    response_1 = await future_1
    response_2 = await future_2

    print(response_1.text)
    print(response_2.text)


def quart_starter():
    app.register_blueprint(SyncQuartEndpoint().quart_blueprint)
    app.register_blueprint(AsyncQuartEndpoint().quart_blueprint)
    app.run(port=8081, host='localhost')


# see: https://stackoverflow.com/questions/22190403/how-could-i-use-requests-in-asyncio
async def main():
    loop = asyncio.get_event_loop()

    t_quart = loop.create_task(quart_starter())
    t_request =loop.create_task(programatic_calls())

    # loop.run_until_complete(t_quart)
    # loop.run_until_complete(t_request)

    loop.run_forever()


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    quart_starter()
