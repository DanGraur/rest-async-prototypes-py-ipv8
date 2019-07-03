from flask import Flask
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from server import FlaskEndpoint

# Create the Flask app
app = Flask(__name__)

# Create an Agent object to send requests
agent = Agent(reactor)


def request_wrapper(endpoint, req_parameter_dict, method=b'GET'):
    url = 'http://localhost:8081/{}/?{}'.format(endpoint, '&'.join(
        ['{}={}'.format(k, v) for k, v in req_parameter_dict.items()])).encode("utf-8")

    print("HERE")
    print("URL = {}\nMETHOD = {}".format(url, method))
    g = agent.request(
        method,
        url,
        headers=Headers({'User-Agent': ['Twisted Web Client Example'],
                         'Content-Type': ['text/x-greeting']}),
        bodyProducer=None
    )
    print("HERE")
    d = g.addCallback(readBody)
    return d


def main():
    my_flask_endpoint = FlaskEndpoint()
    app.register_blueprint(my_flask_endpoint.flask_blueprint)

    root_endpoint = Resource()
    flask_resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    root_endpoint.putChild(b"bottle", flask_resource)

    reactor.listenTCP(8081, Site(root_endpoint), interface="localhost")

    # FIXME: if you use logging messages, it gets stuck somewhere in this yield. Add more messages to find out what
    #        the reason is.
    res = request_wrapper("bottle/flask_endpoint/math", {"op": "add", "a": 2, "b": 3})
    res.addCallback(lambda body: print(body))


if __name__ == '__main__':
    reactor.callWhenRunning(main)
    reactor.run()
