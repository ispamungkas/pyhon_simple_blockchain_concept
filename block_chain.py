import sys
import json
import hashlib
import requests

from datetime import datetime
from uuid import uuid4
from flask import Flask
from flask.globals import request
from flask.json import jsonify
from urllib.parse import urlparse

class BlockChain(object):
    difficult_target = "0000"

    ## Function for hexing the block
    def hash_block(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def valid_proof(self, index, hash_of_previous_block, transaction, nonce):
        content = f'{index}{hash_of_previous_block}{transaction}{nonce}'.encode()
        hash_content = hashlib.sha256(content).hexdigest()
        return hash_content[:len(self.difficult_target)] == self.difficult_target

        
    def proof_of_work(self, index, hash_of_previous_block, transaction):
        nonce = 0
        while self.valid_proof(index, hash_of_previous_block, transaction, nonce) is False:
            nonce += 1
        return nonce
    
    def append_block(self, hash_of_previous_block, nonce):
        t = datetime.now()
        block = {
            'index': len(self.chain),
            'timestamp': t.timestamp(),
            'transaction': self.current_transaction,
            'nonce': nonce,
            'hash_of_previous_block': hash_of_previous_block
        }

        ## Reset transaction when new block is added
        self.current_transaction = []
        self.chain.append(block) ## Adding new block

        return block
    
    def add_transaction(self, sender, recipient, amount_p):
        self.current_transaction.append({
            'amount': amount_p,
            'recipent': recipient,
            'sender': sender
        })
        return self.last_block['index'] + 1
    
    @property
    def last_block(self):
        return self.chain[-1]

    def add_node(self, address):
        url_parse = urlparse(address)
        url_netlock = url_parse.netloc
        self.nodes.add(url_netlock)
        print(url_netlock) ## Check network nodes
    
    def sync_node(self):
        max_length = len(self.chain)
        neighbour = self.nodes
        new_chain = None

        for node in neighbour:
            response = requests.get(f'http://{node}/blockchain')

            if response.status_code is 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
                
                if new_chain:
                    self.chain = new_chain
                    return True
                
        return False

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 0

        while current_index < len(last_block):
            block = chain[current_index]

            if block['hash_of_previous_block'] != self.hash_block(last_block):
                return False
            
            if not self.valid_proof(current_index, block['hash_of_previous_block'], block['transaction'], block['nonce']): return False
            last_block = block
            current_index += 1
        
        return True
        
        
    def __init__(self):
        self.nodes = set()
        self.chain = []
        self.current_transaction = []

        genesis_hash = self.hash_block("genesis_block")

        self.append_block(
            genesis_hash,
            self.proof_of_work(0, genesis_hash, []),
        )


                



                




