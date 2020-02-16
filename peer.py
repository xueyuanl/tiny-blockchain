import json

import requests

from log import logger


class Peer:
    def __init__(self, ipv4, port):
        self.ipv4 = ipv4
        self.port = port

    @property
    def socket(self):
        return self.ipv4 + ':' + self.port

    def to_dict(self):
        return {'ipv4': self.ipv4, 'port': self.port}


class Peers:
    def __init__(self):
        self.me = None
        self.peers = {}

    def add_peers(self, new_peers):
        logger.info('Add peer {} into peers dict'.format(new_peers))
        self.peers[new_peers['ipv4']] = Peer(new_peers['ipv4'], new_peers['port'])

    def generate_peers(self):
        """
        exclude self
        :return: set
        """
        res = []
        res.append(self.me.to_dict())
        res.append([self.peers[p].to_dict() for p in self.peers])
        return res

    @classmethod
    def get_chain(cls, peer):
        response = requests.get('{}server/chain'.format(peer))
        return response.json()['length'], response.json()['chain']

    @classmethod
    def add_block(cls, peer, block):
        url = "{}server/add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        response = requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)
        if response.status_code != 200:
            print('add block to peer {} failed'.format(peer))

    def broadcast_new_peer(self, new_peer):
        logger.info('Begin to broadcast to other peers finding a new peer')
        headers = {'Content-Type': "application/json"}
        for ipv4, peer in self.peers.items():
            logger.info('Send message to peer {}'.format(ipv4))
            data = {'ipv4': new_peer['ipv4'],
                    'port': new_peer['port']}
            response = requests.post('http://' + ipv4 + ':' + peer['port'] + 'server/register_with',
                                     data=json.dumps(data), headers=headers)
            if response.status_code != 200:
                logger.info('broadcast to peer {} failed'.format(ipv4))


peers = Peers()
