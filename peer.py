from log import logger
from utils import call_broadcast_new_peer


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
        res.extend([self.peers[p].to_dict() for p in self.peers])
        return res

    def broadcast_new_peer(self, new_peer):
        logger.info('Begin to broadcast to other peers finding a new peer')
        for ipv4 in self.peers:
            logger.info('Send message to peer {}'.format(ipv4))
            response = call_broadcast_new_peer(new_peer, self.peers[ipv4])
            if response.status_code != 200:
                logger.info('broadcast to peer {} failed'.format(ipv4))


peers = Peers()
