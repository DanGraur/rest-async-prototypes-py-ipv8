from flask import Flask
from twisted.internet import reactor
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
    url = 'http://localhost:8081/{}?{}'.format(endpoint, '&'.join(
        ['{}={}'.format(k, v) for k, v in req_parameter_dict.items()])).encode("utf-8").replace(b' ', b'%20')

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


def main():
    my_flask_endpoint = FlaskEndpoint()
    # Since Flask is stateful, using multiple apps is generally not a common practice (although it is possible)
    # As a consequence, blueprints are employed to register handles in projects with multiple modules
    app.register_blueprint(my_flask_endpoint.flask_blueprint)

    root_endpoint = Resource()
    # A flask app can only be used with Twisted via the WSGIResource. Its handlers do not support asynchronous code.
    flask_resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    root_endpoint.putChild(b"bottle", flask_resource)

    reactor.listenTCP(8081, Site(root_endpoint), interface="localhost")

    # Note the '/' character at the end of the endpoint this is essential for a correct routing since the handler is
    # registered at '/math/' not '/math'
    req_1 = request_wrapper("bottle/flask_endpoint/math/", {"op": "mul", "a": 10, "b": 31})
    req_1.addCallback(lambda response: print(response))

    # There is no '/' character at the end of the uri because the handler was registered under '/echo'
    req_2 = request_wrapper("bottle/flask_endpoint/echo", {"msg": "Hello world!"})
    req_2.addCallback(lambda response: print(response))


if __name__ == '__main__':
    reactor.callWhenRunning(main)
    reactor.run()
