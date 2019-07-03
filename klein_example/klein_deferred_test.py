import json

from klein import Klein

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.task import deferLater
from twisted.web.client import Agent, readBody

from twisted.web.http_headers import Headers
from twisted.web.server import Site

# Create the Klein app
app = Klein()

# Create the HTTP agent
agent = Agent(reactor)


def request_wrapper(endpoint, req_parameter_dict=None, method=b'GET'):
    url = 'http://localhost:8081/{}'.format(endpoint)

    if req_parameter_dict:
        url = url + '?{}'.format('&'.join(['{}={}'.format(k, v) for k, v in req_parameter_dict.items()]))

    url = url.encode("utf-8")
    print(url)
    g = agent.request(
        method,
        url,
        headers=Headers({'User-Agent': ['Twisted Web Client Example'],
                         'Content-Type': ['text/x-greeting']}),
        bodyProducer=None
    )
    d = g.addCallback(readBody)
    return d


@app.route("/sync/")
def simple_synchronous_handler(request):
    return json.dumps({'res': 'success'}).encode('utf-8')


def latent_page(request):
    # request.write(json.dumps({'res': 'It has worked'}).encode('utf-8'))
    # request.finish()
    return json.dumps({'res': 'It has worked'}).encode('utf-8')


@app.route("/async/")
def simple_async_handler(request):
    d = Deferred()
    d.addCallback(latent_page)
    deferLater(reactor, 5, d.callback, request)

    return d


# @app.route("/async/")
# def simple_async_handler(request):
#     return deferLater(reactor, 5, lambda x: json.dumps({'res': x}), "hell yeah")


reactor.listenTCP(8081, Site(app.resource()), interface='localhost')

req_sync = request_wrapper('/async/')
req_sync.addCallback(lambda response: print(response))

reactor.run()
