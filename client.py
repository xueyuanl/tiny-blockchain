from flask import Blueprint
from flask import request

from block import *
from peer import peers

client = Blueprint('client', __name__)


@client.route('/register_node', methods=['POST'])
def register_new_peers():
    # The host address to the peer node
    new_peers = request.get_json()["peers"]
    logger.info('Get a peers list {}'.format(new_peers))
    for n in new_peers:
        if n not in peers.peers:
            logger.info('register a new peer {}'.format(n))
            peers.add_peers(n)

    chain_dump = request.get_json()['chain']
    logger.info('Get a chain dict list {}'.format(chain_dump))
    tmp_blockchain = create_chain_from_dump(chain_dump)
    blockchain.refresh(tmp_blockchain)
    # Return the blockchain to the newly registered node so that it can sync
    return 'Update successful', 200


def create_chain_from_dump(chain_dump):
    # the length of new peer's blockchain ls less than self blockchain
    if len(chain_dump) < len(blockchain.chain):
        logger.info('given blockchain is shorter than self\'s length, return')
        return blockchain
    new_blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data['index'],
                      block_data['transactions'],
                      block_data['timestamp'],
                      block_data['prev_hash'])
        proof = block_data['hash']
        if idx > 0:
            added = new_blockchain.add_block(block, proof)
            if not added:
                raise Exception('The chain dump is tampered!!')
        else:  # the block is a genesis block, no verification needed
            new_blockchain.chain.append(block)
    return new_blockchain
