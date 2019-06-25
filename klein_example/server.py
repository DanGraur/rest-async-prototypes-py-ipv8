import json

from defer import Deferred
from klein import Klein

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import deferLater
from twisted.web.http_headers import Headers
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET, Site
from twisted.web.client import Agent, readBody

# Define the Klein app
app = Klein()
agent = Agent(reactor)


class TestEndpointSync(Resource):
    def render_GET(self, request):
        return json.dumps({'Response': 'You called a synchronous method.'}).encode('utf-8')


class TestEndpointAsync(Resource):
    def latent_callback(self, request):
        request.write(json.dumps({'res': 'It has worked'}).encode('utf-8'))
        request.finish()

    def render_GET(self, request):
        # d = deferLater(request, 0.5, lambda: request)
        # d.addCallback(self.latent_callback)

        d = Deferred()
        d.add_callback(self.latent_callback)
        deferLater(reactor, 2, d.callback, request)

        return d


@app.route('/sync', methods=['GET', 'POST'])
def sync_method(request):
    return json.dumps({'Response': 'You called a synchronous method.'}).encode('utf-8')


@app.route('/async', methods=['GET', 'POST'], branch=True)
def async_method(request):

    # Could it be that Klein is closing my request
    def simulate_workload(call_count):
        if call_count > 3:
            request.write(json.dumps({'Response': 'You called an asynchronous method.'}).encode('utf-8'))
            request.finish()
        else:
            print("Hello from async {}".format(call_count))

            d = Deferred()
            d.add_callback(simulate_workload)
            deferLater(reactor, 0.5, d.callback, call_count + 1)

            return NOT_DONE_YET

    deferLater(reactor, 0.5, simulate_workload, 1)

    return NOT_DONE_YET


def latent_page(request):
    request.write(json.dumps({'res': 'It has worked'}).encode('utf-8'))
    request.finish()


@app.route('/async_two', methods=['GET', 'POST'], branch=True)
def async_method_two(request):
    # d = deferLater(reactor, 2, lambda: request)
    # d.addCallback(latent_page)

    d = Deferred()
    d.add_callback(latent_page)
    deferLater(reactor, 2, d.callback, request)

    return NOT_DONE_YET


@inlineCallbacks
def send_request(endpoint, method=b'GET'):
    g = agent.request(
        method,
        'http://localhost:8081/{}'.format(endpoint).encode('utf-8'),
        Headers({'User-Agent': ['Twisted Web Client Example'],
                 'Content-Type': ['text/x-greeting']})
    )
    response = yield g.addCallback(readBody)
    returnValue(response)


def twisted_init():
    """Set up a Twisted REST API"""
    root_endpoint = Resource()
    root_endpoint.putChild(b"oldasync", TestEndpointAsync())
    root_endpoint.putChild(b"oldsync", TestEndpointSync())

    reactor.listenTCP(8081, Site(root_endpoint), interface='localhost')


def klein_init():
    """Set up a Klein REST API"""
    root_endpoint = Resource()
    root_endpoint.putChild(b'new', app.resource())

    reactor.listenTCP(8081, Site(root_endpoint), interface='localhost')
    # reactor.listenTCP(8081, Site(app.resource()), interface='localhost')


@inlineCallbacks
def main():
    use_klein = True

    if not use_klein:
        twisted_init()
        endpoint = 'oldasync'
    else:
        klein_init()
        endpoint = 'new/async_two'

    res = send_request(endpoint)
    res.addCallback(lambda body: print(body))
    reactor.run()


if __name__ == '__main__':
    main()

# TODO: Yeah so the problem is from Klein; It doesn't really know how to handle the NOT_DONE_YET. Maybe it uses some
#       other form of signaling for an async method (the async keyword??)
