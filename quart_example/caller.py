import asyncio
from threading import Thread

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


def programatic_calls_wrapper(loop):
    asyncio.set_event_loop(loop)
    asyncio.sleep(5)

    task_1 = loop.create_task(programatic_calls())
    loop.run_until_complete(task_1)


def quart_starter(loop):
    asyncio.set_event_loop(loop)
    app.register_blueprint(SyncQuartEndpoint().quart_blueprint)
    app.register_blueprint(AsyncQuartEndpoint().quart_blueprint)
    app.run(port=8081, host='localhost')


# see: https://stackoverflow.com/questions/22190403/how-could-i-use-requests-in-asyncio
def main():
    # quart_starter_thread = Thread(target=quart_starter, args=(asyncio.get_event_loop(), ))
    # quart_starter_thread.start()

    # time.sleep(4)
    # asyncio.sleep(4)

    programatic_req_thread = Thread(target=programatic_calls_wrapper, args=(asyncio.get_event_loop(), ))
    programatic_req_thread.start()

    app.register_blueprint(SyncQuartEndpoint().quart_blueprint)
    app.register_blueprint(AsyncQuartEndpoint().quart_blueprint)
    app.run(port=8081, host='localhost')


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # quart_starter()
    # main()

    app.register_blueprint(SyncQuartEndpoint().quart_blueprint)
    app.register_blueprint(AsyncQuartEndpoint().quart_blueprint)
    app.run(port=8081, host='localhost')

    # FIXME: for some reason, this will yield 'RuntimeError: set_wakeup_fd only works in main thread'
    #        look into a mock server: https://github.com/aio-libs/aiohttp/blob/master/examples/fake_server.py
    #        Also, I think running https://aiohttp.readthedocs.io/en/stable/ (that is, aiohttp) could be more powerful
    #        Also, talk to Quinten about your progress and tell Johan about the flexdelft account, and the internship

    # TODO:  Also, don't forget, there definitely is a way of sending requests programatically (from another thread
    #        for instance, or another process altogether)
    #        MUST (I THINK THIS HAS THE ANSWERS I NEED): Also, look at https://stackoverflow.com/questions/54370505/python-asyncio-skip-processing-untill-function-return
