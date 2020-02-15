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


def broadcast_to_peers(new_peer, peers):
    headers = {'Content-Type': "application/json"}
    for peer in peers:
        data = {"Node_address": new_peer}
        response = requests.post(peer + "server/register_with", data=json.dumps(data), headers=headers)


peers = Peers()
