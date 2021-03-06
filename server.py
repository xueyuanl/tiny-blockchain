from flask import Blueprint
from flask import request

from block import *
from log import logger
from peer import peers, Peer
from utils import call_register_callback

SERVER_URL_PREFIX = '/server'
server = Blueprint(SERVER_URL_PREFIX, __name__)

NEW_TRANSACTION = '/new_transaction'
PENDING_TRANSACTION = '/pending_tx'
MINE = '/mine'
CHAIN = '/chain'
REGISTER_NODE = '/register_with'
NEW_BLOCK = '/add_block'


@server.route(NEW_TRANSACTION, methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ['author', 'content']

    for field in required_fields:
        if not tx_data.get(field):
            logger.info('Given an invalid transaction data')
            return 'Invalid transaction data', 404

    tx_data['timestamp'] = time.time()
    logger.info('Come to add transaction')
    blockchain.add_new_transaction(tx_data)

    return 'Success', 201


@server.route(MINE, methods=['GET'])
def mine_unconfirmed_transactions():
    mined_block = blockchain.mine()
    if not mined_block:
        return 'No transactions to mine'
    logger.info('Mined a new block {}, try to consensus with other peers.'.format(mined_block))
    # Making sure we have the longest chain before announcing to the network
    if blockchain.consensus(peers.peers):
        logger.info('Got a longer chain from other peers, skip to mine.')
        return 'No transactions to mine'
    # we mined a block, and we have the longest blockchain, so announce to the network
    blockchain.announce_block(peers.peers)
    return 'Block {} is mined.'.format(mined_block)


@server.route(PENDING_TRANSACTION)
def pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


@server.route(CHAIN, methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


@server.route(REGISTER_NODE, methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the remote node specified in the
    request, and sync the blockchain as well with the remote node.
    """
    ipv4 = request.get_json()['ipv4']
    new_peer_dict = request.get_json()
    logger.info('Receive a new peer {} register request'.format(ipv4))
    if ipv4 in peers.peers:
        logger.info('New peer is already registered')
        return 'Already registered', 200

    socket = request.host_url[7:-1].split(':')
    peers.me = Peer(socket[0], socket[1])

    data = {'peers': peers.generate_peers(),
            'chain': [block.__dict__ for block in blockchain.chain]}
    response = call_register_callback(new_peer_dict, data)

    if response.status_code != 200:
        logger.info('Fail to get response from new peer, status code {}'.format(response.status_code))
        return response.content, response.status_code

    peers.broadcast_new_peer(new_peer_dict)
    peers.add_peer(new_peer_dict)
    return 'Registration successful', 200


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@server.route(NEW_BLOCK, methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["prev_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        logger.info('Failed to add the block {}'.format(block_data))
        return "The block was discarded by the node", 400
    logger.info('Success to add the block {}'.format(block_data))
    return "Block added to the chain", 201
