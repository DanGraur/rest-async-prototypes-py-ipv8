import json
import random

from klein import Klein
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
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
        # return pack_http_response({"Req args": request.args})

        op = request.args.get(b"op", ["add"])[0]
        a = request.args.get(b"a", [None])[0]
        b = request.args.get(b"b", [None])[0]

        # Handle the errors
        if not a or not b:
            request.setResponseCode(http.BAD_REQUEST)
            return pack_http_response({'result': "Error: one or both variables were not specified by the request"})

        a = int(a)
        b = int(b)

        op = op.decode('utf-8').lower()

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
        msg = request.args.get(b"msg", [None])[0]

        if msg:
            return pack_http_response({"echo": msg.decode('utf-8')})
        else:
            return pack_http_response({'result': "Error: no message was specified"})


class AsyncKleinEndpoint:
    # Since Klein apps are stateless, it is possible to use multiples such instances to facilitate multi module projects
    async_klein_endpoint = Klein()

    @async_klein_endpoint.route("/math")
    def asynchronous_math(self, request):
        # return pack_http_response({"Req args": request.args})
        # Flask uses a default request object, which holds the request info
        op = request.args.get(b"op", ["add"])[0]
        a = request.args.get(b"a", [None])[0]
        b = request.args.get(b"b", [None])[0]

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

                    # The deferreds always need to be returned in Klein; if they are not, Twisted throws an error
                    # which states that the write() is called on a request which is finished. This happens because
                    # Klein calls finish() on a request implicitly, if no deferred is returned.
                    return d

            return inner_math

        d = Deferred()
        d.addCallback(inner_math_curried(op.decode('utf-8').lower(), int(a), int(b)))
        deferLater(reactor, 1, d.callback, 0)

        return d

    @async_klein_endpoint.route("/echo")
    def asynchronous_echo(self, request):
        msg = request.args.get(b"msg", [None])[0]

        if not msg:
            request.setResponseCode(http.BAD_REQUEST)
            return pack_http_response({'result': "Error: no message was specified"})

        def echo(msg):
            request.write(pack_http_response({"echo": msg.decode('utf-8')}))
            request.finish()

        d = deferLater(reactor, 1, echo, msg)
        return d

    @async_klein_endpoint.route("/parallel")
    def run_in_parallel(self, request):
        some_random_words = [
            "gel",
            "mine",
            "car",
            "soap",
            "umbrella",
            "variable",
            "function",
            "type",
            "wheel",
            "bird",
            "around"
        ]

        def random_word():
            return some_random_words[random.randint(0, len(some_random_words) - 1)]

        def final_deferred(res_list):
            request.write(pack_http_response({"res": " ".join([x[1] for x in res_list])}))
            request.finish()

        run_count = 10
        deferred_list = []

        for i in range(run_count):
            deferred_list.append(deferLater(reactor, random.uniform(1.0, 2.0), random_word))

        d = DeferredList(deferred_list)
        d.addCallback(final_deferred)
        return d
