from quart import Quart
from server import AsyncQuartEndpoint, SyncQuartEndpoint

app = Quart(__name__)


def main():
    app.register_blueprint(SyncQuartEndpoint().quart_blueprint)
    app.register_blueprint(AsyncQuartEndpoint().quart_blueprint)
    app.run(port=8081, host='localhost')


if __name__ == '__main__':
    main()
