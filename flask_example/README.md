# Instructions

The following instructions describe how to start up a Quart based server, and forward requests to it:

1. run `python caller.py`

The latter instruction will send out 2 synchronous requests. 

Additional requests may be sent to the uri: `localhost:8081/flask/flask_endpoint/<echo|math>?<args>`.   

## Dependencies

The following are the dependencies for this demo:

```bash
Twisted
flask
```

