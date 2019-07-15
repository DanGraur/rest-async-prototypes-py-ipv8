import asyncio
import requests


run_forever = True


def attach_print_callback(f):
    f.add_done_callback(lambda x: print(x.result().text))


async def send_requests(loop=None):

    # If no loop is provided, get the default loop.
    if not loop:
        loop = asyncio.get_event_loop()

    # Sync Requests
    attach_print_callback(loop.run_in_executor(None, requests.get, 'http://localhost:8081/sync/math?a=1&b=3&op=div'))
    attach_print_callback(loop.run_in_executor(None, requests.get, 'http://localhost:8081/sync/echo?msg=(Sync)%20'
                                                                   'this%20is%20a%20message.'))

    # Async Requests
    attach_print_callback(loop.run_in_executor(None, requests.get, 'http://localhost:8081/async/math?a=123&b=3&op=mul'))
    attach_print_callback(loop.run_in_executor(None, requests.get, 'http://localhost:8081/async/echo?msg=(Async)%20'
                                                                   'this%20is%20a%20message.'))


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_requests())

    if run_forever:
        loop.run_forever()
    else:
        pass


if __name__ == '__main__':
    main()
