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


counter = 0


def latent_page(request):
    global counter
    counter += 1
    if counter % 3 == 0:
        print("IN final latent_page", counter)
        request.write(json.dumps({'res': 'It has worked'}).encode('utf-8'))
        request.finish()
    else:
        print("IN latent_page", counter)

        d = Deferred()
        d.addCallback(latent_page)
        deferLater(reactor, 2, d.callback, request)

        return d


@app.route("/async/")
def simple_async_handler(request):
    print(request)
    print(type(request))

    d = Deferred()
    d.addCallback(latent_page)
    deferLater(reactor, 2, d.callback, request)

    print("IN simple_async_handler")

    return d


# @app.route("/async/")
# def simple_async_handler(request):
#     return deferLater(reactor, 5, lambda x: json.dumps({'res': x}), "hell yeah")


reactor.listenTCP(8081, Site(app.resource()), interface='localhost')

try:
    req_sync = request_wrapper('async/')
    req_sync.addCallback(lambda response: print(response))
except Exception as e:
    print(e)

reactor.run()

# TODO: YOU CANNOT PASS STATE WHEN DEFERRING WITH KLEIN: I could not pass an additional argument to the deferred's
# callback, other than the request object itself. I could only pass the state via a global variable; is it possible
# to send state via the request object

# Also, from the Klein docs, and why I think the Deferred object itself is used rather than a NOT_DONE_YET:
#       And of course, this is Twisted. So there is a wealth of APIs that return a Deferred. A Deferred may also be
#       returned from handler functions and their result will be used as the response body.
