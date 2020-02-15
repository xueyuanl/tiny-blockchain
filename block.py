import json
import time
from hashlib import sha256

from peer import Peers


class Block:
    def __init__(self, index, transactions, timestamp, prev_hash, nonce=0):
        """
        Constructor for the `Block` class.
        :param index: Unique ID of the block.
        :param transactions: List of transactions.
        :param timestamp: Time of generation of the block.
        :param prev_hash: Hash of the previous block in the chain which this block is part of.
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.prev_block = None
        self.hash = None

    def compute_hash(self):
        """
        Returns the hash of the block instance by first converting it
        into JSON string.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # difficulty of PoW algorithm
    difficulty = 2

    def __init__(self):
        """
        Constructor for the 'Blockchain' class.
        """
        self.unconfirmed_transactions = []  # data yet to get into blockchain
        self.chain = []

    def refresh(self, blockchain):
        """
        use another blockchain to replace self
        :param blockchain:
        :return:
        """
        self.unconfirmed_transactions = blockchain.unconfirmed_transactions
        self.chain = blockchain.chain

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        return self

    @property
    def last_block(self):
        """
        A quick pythonic way to retrieve the most recent block in the chain. Note that
        the chain will always consist of at least one block (i.e., genesis block)
        """
        return self.chain[-1]

    def proof_of_work(self, block):
        """
        Function that tries different values of the nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_block(self, block, computed_hash):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of a latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_hash_value(block, computed_hash):
            return False

        block.hash = computed_hash
        self.chain.append(block)
        return True

    @classmethod
    def is_valid_hash_value(cls, block, computed_hash):
        """
        proof of work.
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (computed_hash.startswith('0' * Blockchain.difficulty) and
                computed_hash == block.compute_hash())

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out proof of work.
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          prev_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index

    @classmethod
    def check_chain_validity(cls, chain):
        """
        A helper method to check if the entire blockchain is valid.
        """
        result = True
        previous_hash = '0'

        # Iterate through every block
        for block in chain:
            block_hash = block.hash

            if not cls.is_valid_hash_value(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            previous_hash = block_hash

        return result

    def consensus(self, peers):
        """
        Our naive consnsus algorithm. If a longer valid chain is
        found, our chain is replaced with it.
        """

        longest_chain = None
        current_len = len(self.chain)

        for peer in peers:
            length, chain = Peers.get_chain(peer)
            if length > current_len and blockchain.check_chain_validity(chain):
                current_len = length
                longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False

    def announce_block(self, peers):
        """
            A function to announce to the network once a block has been mined.
            Other blocks can simply verify the proof of work and add it to their
            respective chains.
            """
        for peer in peers:
            Peers.add_block(peer, self.last_block)


blockchain = Blockchain().create_genesis_block()
