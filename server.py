import requests
from flask import Blueprint
from flask import request

from block import *
from peer import peers

server = Blueprint('server', __name__)


@server.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ['author', 'content']

    for field in required_fields:
        if not tx_data.get(field):
            return 'Invalid transaction data', 404

    tx_data['timestamp'] = time.time()

    blockchain.add_new_transaction(tx_data)

    return 'Success', 201


@server.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return 'No transactions to mine'

    # Making sure we have the longest chain before announcing to the network
    if blockchain.consensus(peers):
        # we get a longer chain from other peers
        return 'No transactions to mine'
    # we mined a block, and we have the longest blockchain, so announce to the network

    return 'Block #{} is mined.'.format(result)


@server.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


@server.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


@server.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the remote node specified in the
    request, and sync the blockchain as well with the remote node.
    """
    new_peer_addr = request.get_json()['node_address']  # sample: http://192.168.1.2:2008/
    if not new_peer_addr:
        return 'Invalid data', 400
    if new_peer_addr in peers.peers:
        return 'Already registered', 200

    peers.me = request.host_url

    data = {'peers': list(peers.generate_peers()),
            'chain': [block.__dict__ for block in blockchain.chain]}
    headers = {'Content-Type': 'application/json'}

    # send to client, to help the client update the peers list and build the blockchain
    response = requests.post(new_peer_addr + '/client/register_node', data=json.dumps(data), headers=headers)

    if response.status_code != 200:
        return response.content, response.status_code
    peers.broadcast_new_peer(new_peer_addr)
    peers.add_peers(new_peer_addr)
    return 'Registration successful', 200


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@server.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201
