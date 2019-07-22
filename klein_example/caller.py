from klein import Klein
from server import AsyncKleinEndpoint, SyncKleinEndpoint

from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.web.server import Site


app = Klein()
agent = Agent(reactor)


@app.route("/sync", branch=True)
def redirect_sync(request):
    return SyncKleinEndpoint().sync_klein_endpoint.resource()


@app.route("/async", branch=True)
def redirect_async(request):
    return AsyncKleinEndpoint().async_klein_endpoint.resource()


def request_wrapper(endpoint, req_parameter_dict=None, method=b'GET'):
    if req_parameter_dict:
        url = 'http://localhost:8081/{}?{}'.format(endpoint, '&'.join(
            ['{}={}'.format(k, v) for k, v in req_parameter_dict.items()])).encode("utf-8").replace(b' ', b'%20')
    else:
        url = 'http://localhost:8081/{}'.format(endpoint).encode("utf-8").replace(b' ', b'%20')

    # print(url)
    g = agent.request(
        method,
        url,
        headers=Headers({'User-Agent': ['Twisted Web Client Example'],
                         'Content-Type': ['text/x-greeting']}),
        bodyProducer=None
    )
    d = g.addCallback(readBody)
    return d


def main():
    reactor.listenTCP(8081, Site(app.resource()), interface="localhost")

    req_1 = request_wrapper("sync/math", {"op": "mul", "a": 10, "b": 31})
    req_1.addCallback(lambda response: print(response))

    req_2 = request_wrapper("sync/echo", {"msg": "Hello world Sync!"})
    req_2.addCallback(lambda response: print(response))

    req_3 = request_wrapper("async/math", {"op": "div", "a": 10, "b": 31})
    req_3.addCallback(lambda response: print(response))

    req_4 = request_wrapper("async/echo", {"msg": "Hello world Async!"})
    req_4.addCallback(lambda response: print(response))

    req_5 = request_wrapper("async/parallel")
    req_5.addCallback(lambda response: print(response))


if __name__ == '__main__':
    reactor.callWhenRunning(main)
    reactor.run()
