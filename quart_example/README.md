# Instructions

The following instructions describe how to start up a Quart based server, and forward requests to it:

1. run `python start.py`
2. run `python caller.py`

The latter instruction will send out  4 requests. The first 2 synchronous, and the latter 2 asynchronous.

Additional requests may be sent to the uri: `localhost:8081/<sync|async>/<math|echo>?<args>`.

## Dependencies

The following are the dependencies for this demo:

```bash
Quart
```
