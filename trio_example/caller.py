import asks
import trio


async def send_request(uri):
    res = await asks.get(uri)
    print(res.json())


async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(send_request, "http://localhost:8081/sync/echo?msg=This%20is%20a%20sync%20message.")
        nursery.start_soon(send_request, "http://localhost:8081/sync/math?op=add&a=3&b=4")
        nursery.start_soon(send_request, "http://localhost:8081/async/math?op=div&a=123&b=4")
        nursery.start_soon(send_request, "http://localhost:8081/async/echo?msg=This%20is%20an%20async%20message.")
        nursery.start_soon(send_request, "http://localhost:8081/async/parallel")


if __name__ == '__main__':
    trio.run(main)
