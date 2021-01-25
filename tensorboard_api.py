import os

import flask
import tensorboard as tb
from werkzeug import serving
from werkzeug.middleware import dispatcher

HOST = "0.0.0.0"
PORT = 8080

flask_app = flask.Flask(__name__)


@flask_app.route("/hello-world", methods=["GET", "POST"])
def say_hello():
    return flask.jsonify({"result": "Hello world"})


class CustomServer(tb.program.TensorBoardServer):
    def __init__(self, tensorboard_app, flags):
        del flags  # unused
        self._app = dispatcher.DispatcherMiddleware(
            flask_app, {"/tensorboard": tensorboard_app}
        )

    def serve_forever(self):
        serving.run_simple(HOST, PORT, self._app)

    def get_url(self):
        return "http://%s:%s" % (HOST, PORT)

    def print_serving_message(self):
        pass  # Werkzeug's `serving.run_simple` handles this


def main():
    program = tb.program.TensorBoard(server_class=CustomServer)
    program.configure(logdir=os.path.expanduser("logs/fit"))
    program.main()


if __name__ == "__main__":
    main()