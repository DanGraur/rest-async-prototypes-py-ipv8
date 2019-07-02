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


@inlineCallbacks
def send_request(url, method=b'GET'):
    print("Method: {}\nURL: {}".format(method, url))
    g = agent.request(
        method,
        url,
        Headers({'User-Agent': ['Twisted Web Client Example'],
                 'Content-Type': ['text/x-greeting']}),
        None
    )
    body = yield g.addCallback(readBody)
    returnValue(body)
    # g.addCallback(readBody)
    # return g


@inlineCallbacks
def request_wrapper(endpoint, req_parameter_dict, method=b'GET'):
    url = 'http://localhost:8081/{}?{}'.format(endpoint, '&'.join(
        ['{}={}'.format(k, v) for k, v in req_parameter_dict.items()]))
    response = yield send_request(url.encode('utf_8'), method=method)
    returnValue(response)


def main():
    my_flask_endpoint = FlaskEndpoint()
    app.register_blueprint(my_flask_endpoint.flask_blueprint)

    root_endpoint = Resource()
    flask_resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    root_endpoint.putChild(b"bottle", flask_resource)

    reactor.listenTCP(8081, Site(root_endpoint), interface="localhost")

    res = request_wrapper("bottle/flask_endpoint/math", {"op": "add", "a": 2, "b": 3})
    res.addCallback(lambda body: print(body))
    # print(res)
    # print("HERE")
    reactor.stop()


if __name__ == '__main__':
    reactor.callWhenRunning(main)
    reactor.run()

