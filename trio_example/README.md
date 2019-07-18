# Instructions

**Note that this example makes use of Python 3.7 since Quart-Trio does not provide support for Python 3.6.**

The following instructions describe how to start up a Quart based server, and forward requests to it:

1. run `python3.7 start.py`
2. run `python3.7 caller.py`

The latter instruction will send out 5 requests. The first 2 synchronous, and the latter 3 asynchronous.

Additional requests may be sent to the uri: `localhost:8081/<sync|async>/<math|echo|parallel>(?<args>)?`.

## Dependencies

The following are the dependencies for this demo:

```bash
python3.7
trio
asks            # Asynchronous request library for Trio
Quart-Trio      # Port of Quart for Trio
```

