import json
from klein import Klein
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.task import deferLater
from twisted.web import http


def pack_http_response(data):
    return json.dumps(data).encode('utf-8')


class SyncKleinEndpoint:
    # Define the Kelin app as a class variable, and use it to register handlers
    sync_klein_endpoint = Klein()

    @sync_klein_endpoint.route("/math")
    def synchronous_math(self, request):
        # Flask uses a default request object, which holds the request info
        op = request.args.get(b"op", "add")
        a = request.args.get(b"a", None)
        b = request.args.get(b"b", None)

        # Handle the errors
        if not a or not b:
            request.setResponseCode(http.BAD_REQUEST)
            return pack_http_response({'result': "Error: one or both variables were not specified by the request"})

        a = int(a)
        b = int(b)

        op = op.lower()

        if op == "add":
            return pack_http_response({'result': a + b})
        elif op == "sub":
            return pack_http_response({'result': a - b})
        elif op == "mul":
            return pack_http_response({'result': a * b})
        else:
            return pack_http_response({'result': a / b})

    @sync_klein_endpoint.route("/echo")
    def synchronous_echo(self, request):
        msg = request.args.get("msg", None)

        if msg:
            return pack_http_response({"echo": msg})
        else:
            return pack_http_response({'result': "Error: no message was specified"})


class AsyncKleinEndpoint:
    # Since Klein apps are stateless, it is possible to use multiples such instances to facilitate multi module projects
    async_klein_endpoint = Klein()

    @async_klein_endpoint.route("/math")
    def asynchronous_math(self, request):
        # Flask uses a default request object, which holds the request info
        op = request.args.get("op", "add")
        a = request.args.get("a", None)
        b = request.args.get("b", None)

        # Handle the errors
        if not a or not b:
            request.setResponseCode(http.BAD_REQUEST)
            return pack_http_response({'result': "Error: one or both variables were not specified by the request"})

        def inner_math_curried(op, a, b):
            def inner_math(count):
                count += 1

                if count == 2:
                    if op == "add":
                        request.write(pack_http_response({'result': a + b}))
                    elif op == "sub":
                        request.write(pack_http_response({'result': a - b}))
                    elif op == "mul":
                        request.write(pack_http_response({'result': a * b}))
                    else:
                        request.write(pack_http_response({'result': a / b}))
                    request.finish()
                else:
                    d = Deferred()
                    d.addCallback(inner_math)
                    deferLater(reactor, 1, d.callback, count)

            return inner_math

        d = Deferred()
        d.addCallback(inner_math_curried(op.lower(), int(a), int(b)))
        deferLater(reactor, 1, d.callback, 0)

        return d

    @async_klein_endpoint.route("/echo")
    def asynchronous_echo(self, request):
        msg = request.args.get("msg", None)

        if not msg:
            request.setResponseCode(http.BAD_REQUEST)
            return pack_http_response({'result': "Error: no message was specified"})

        def echo(msg):
            request.write(pack_http_response({"echo": msg}))
            request.finish()

        d = deferLater(reactor, 2, echo, msg)
        return d
