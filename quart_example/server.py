import asyncio
import random

from quart.blueprints import Blueprint
from quart import request, jsonify


class SyncQuartEndpoint:

    def __init__(self):
        # Create an blueprint object like in Flask
        self.quart_blueprint = Blueprint('SyncQuartEndpoint', __name__, url_prefix="/sync")

        # Register some handlers
        self.quart_blueprint.add_url_rule("/math", 'sync_quick_maths', self.quick_maths)
        self.quart_blueprint.add_url_rule("/echo", 'sync_echo', self.echo)

    def quick_maths(self):
        op = request.args.get("op", None)
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

    def echo(self):
        msg = request.args.get("msg", None)

        if msg:
            return jsonify({"echo": msg})
        else:
            return jsonify({'result': "Error: no message was specified"})


class AsyncQuartEndpoint:

    def __init__(self):
        # Create an blueprint object like in Flask
        self.quart_blueprint = Blueprint('AsyncQuartEndpoint', __name__, url_prefix="/async")

        # Register some handlers
        self.quart_blueprint.add_url_rule("/math", 'async_quick_maths', self.quick_maths)
        self.quart_blueprint.add_url_rule("/echo", 'async_echo', self.echo)
        self.quart_blueprint.add_url_rule("/parallel", 'async_parallel', self.run_in_parallel)

    async def simulate_work(self, duration=1):
        await asyncio.sleep(duration)

    async def quick_maths(self):
        op = request.args.get("op", None)
        a = request.args.get("a", None)
        b = request.args.get("b", None)

        # Handle the errors
        if not a or not b:
            return jsonify({'result': "Error: one or both variables were not specified by the request"})

        a = int(a)
        b = int(b)

        op = op.lower()

        def inner_math_curried(op, a, b):
            async def inner_math(count):
                count += 1

                if count == 3:
                    if op == "add":
                        return jsonify({'result': a + b})
                    elif op == "sub":
                        return jsonify({'result': a - b})
                    elif op == "mul":
                        return jsonify({'result': a * b})
                    else:
                        return jsonify({'result': a / b})
                else:

                    await self.simulate_work(2)

                    return await inner_math(count)

            return inner_math

        return await inner_math_curried(op, a, b)(0)

    async def echo(self):
        msg = request.args.get("msg", None)

        if not msg:
            return jsonify({'result': "Error: no message was specified"})

        await self.simulate_work(2)

        return jsonify({"echo": msg})

    async def run_in_parallel(self):
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

        async def inner_parallel(my_id, result_dict):
            await self.simulate_work(random.uniform(1.0, 2.0))

            result_dict[my_id] = some_random_words[random.randint(0, len(some_random_words) - 1)]

        run_count = 10
        result_dict = dict()

        # https://stackoverflow.com/questions/42231161/asyncio-gather-vs-asyncio-wait
        await asyncio.gather(*[inner_parallel(i, result_dict) for i in range(run_count)])

        return jsonify({'result': " ".join([result_dict[i] for i in range(run_count)])})
