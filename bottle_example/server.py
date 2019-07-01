from flask import Blueprint, request
from flask.json import jsonify


class FlaskEndpoint:

    def __init__(self):
        # The parameters have the following semantics:
        #   - first parameter: a unique name for this instance of the blueprint class
        #   - the second is the instance's import name
        #   - url_prefix: a prefix which is prepended to all request urls registered with the blueprint
        self.flask_blueprint = Blueprint('FlaskEndpoint_Blueprint', __name__, url_prefix="/flask_endpoint")

        # Register a request handler associated to the specified url
        self.flask_blueprint.add_url_rule("/math/", "simple_synchronous_handler", self.simple_synchronous_handler)
        self.flask_blueprint.add_url_rule("/echo/", "simple_synchronous_echo", self.simple_synchronous_echo)

    def simple_synchronous_handler(self):
        # Flask uses a default request object, which holds the request info
        op = request.args.get("op", "add")
        a = request.args.get("a", None)
        b = request.args.get("b", None)

        # Handle the errors
        if not a or not b:
            return jsonify({'result': "Error: one or both variables were not specified by the request"})

        a = int(a)
        b = int(b)

        op = op.lower()

        if op == "add":
            return jsonify({'result': a + b})
        elif op == "sub":
            return jsonify({'result': a - b})
        elif op == "mul":
            return jsonify({'result': a * b})
        else:
            return jsonify({'result': a / b})

    def simple_synchronous_echo(self, msg):
        return jsonify({"Echo": msg})
