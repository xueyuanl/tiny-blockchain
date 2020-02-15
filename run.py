from flask import Flask

from client import client
from server import server

app = Flask(__name__)
app.register_blueprint(server, url_prefix='/server')
app.register_blueprint(client, url_prefix='/client')


def main():
    app.run(host='0.0.0.0', port=2008, debug=True)


if __name__ == '__main__':
    main()
