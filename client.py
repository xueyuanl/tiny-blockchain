from flask import Blueprint
from flask import request

from block import *
from peer import peers

client = Blueprint('client', __name__)


@client.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers.generate_peers())})


# Endpoint to add new peers to the network
@client.route('/register_node', methods=['POST'])
def register_new_peers():
    # The host address to the peer node
    new_peers = request.get_json()["peers"]
    if not new_peers:
        return "Invalid data", 400

    if new_peers in peers.peers:
        return 'Already in my peers list', 201
    # Add the node to the peer list
    peers.add_peers(new_peers)

    # Return the blockchain to the newly registered node so that it can sync
    return get_chain()
