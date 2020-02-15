import requests
from flask import Blueprint
from flask import request

from block import *
from peer import peers, broadcast_to_peers

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
    return 'Block #{} is mined.'.format(result)


@server.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


@server.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the remote node specified in the
    request, and sync the blockchain as well with the remote node.
    """
    new_peer_addr = request.get_json()['node_address']
    if not new_peer_addr:
        return 'Invalid data', 400
    if new_peer_addr in peers.peers:
        return 'Already registered', 200

    peers.me = request.host_url

    data = {'peers': peers.generate_peers()}
    headers = {'Content-Type': 'application/json'}

    # Make a request to register with remote node and obtain information
    response = requests.post(new_peer_addr + '/client/register_node', data=json.dumps(data), headers=headers)

    if response.status_code != 200:
        return response.content, response.status_code

    # update chain and the peers
    # chain_dump = response.json()['chain']
    # tmp_blockchain = create_chain_from_dump(chain_dump)
    # blockchain.refresh(tmp_blockchain)
    broadcast_to_peers(new_peer_addr, peers.generate_peers())
    peers.add_peers(new_peer_addr)
    return 'Registration successful', 200


def create_chain_from_dump(chain_dump):
    # the length of new peer's blockchain ls less than self blockchain
    if len(chain_dump) < len(blockchain.chain):
        return blockchain
    new_blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data['index'],
                      block_data['transactions'],
                      block_data['timestamp'],
                      block_data['previous_hash'])
        proof = block_data['hash']
        if idx > 0:
            added = new_blockchain.add_block(block, proof)
            if not added:
                raise Exception('The chain dump is tampered!!')
        else:  # the block is a genesis block, no verification needed
            new_blockchain.chain.append(block)
    return new_blockchain
