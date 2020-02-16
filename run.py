from flask import Flask

from client import client, CLIENT_URL_PREFIX
from log import logger
from server import server, SERVER_URL_PREFIX

app = Flask(__name__)
app.register_blueprint(server, url_prefix=SERVER_URL_PREFIX)
app.register_blueprint(client, url_prefix=CLIENT_URL_PREFIX)


def main():
    logger.info('start...')
    app.run(host='0.0.0.0', port=2008, debug=True)


if __name__ == '__main__':
    main()
