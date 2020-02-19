import json

import requests

from log import logger


def call_register_callback(node, data):
    from client import CLIENT_URL_PREFIX, REGISTER_CALLBACK
    headers = {'Content-Type': 'application/json'}
    logger.info('Send back to new peer, the data is {}'.format(data))
    # send to client, to help the client update the peers list and build the blockchain
    url = 'http://{}:{}{}{}'.format(node['ipv4'], str(node['port']), CLIENT_URL_PREFIX, REGISTER_CALLBACK)
    logger.info('call url {}'.format(url))
    return requests.post(url, data=json.dumps(data), headers=headers)


def call_broadcast_new_peer(new_peer, broadcast_peer):
    from client import CLIENT_URL_PREFIX, NEW_PEER
    headers = {'Content-Type': "application/json"}
    data = {'ipv4': new_peer['ipv4'], 'port': new_peer['port']}
    url = 'http://{}:{}{}{}'.format(broadcast_peer.ipv4, str(broadcast_peer.port), CLIENT_URL_PREFIX, NEW_PEER)
    logger.info('call url {}'.format(url))
    return requests.post(url, data=json.dumps(data), headers=headers)


def call_add_block(peer, block):
    from server import SERVER_URL_PREFIX, NEW_BLOCK
    headers = {'Content-Type': "application/json"}
    url = 'http://{}:{}{}{}'.format(peer.ipv4, str(peer.port), SERVER_URL_PREFIX, NEW_BLOCK)
    logger.info('call url {}'.format(url))
    return requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)


def call_get_chain(peer):
    from server import SERVER_URL_PREFIX, CHAIN
    url = 'http://{}:{}{}{}'.format(peer.ipv4, str(peer.port), SERVER_URL_PREFIX, CHAIN)
    logger.info('call url {}'.format(url))
    response = requests.get(url)
    return response.json()['length'], response.json()['chain']
