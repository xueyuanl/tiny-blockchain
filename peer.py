import copy
import json

import requests


class Peers:
    def __init__(self):
        self.me = None
        self.peers = set()

    def add_peers(self, new_peers):
        self.peers.add(new_peers)

    def generate_peers(self):
        """
        exclude self
        :return: set
        """
        res = copy.copy(self.peers)
        res.add(self.me)
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
        headers = {'Content-Type': "application/json"}
        for peer in self.peers:
            data = {"Node_address": new_peer}
            response = requests.post(peer + "server/register_with", data=json.dumps(data), headers=headers)
            if response.status_code != 200:
                print('broadcast to peer {} failed'.format(peer))


peers = Peers()
