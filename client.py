import uuid
import sys
from flask import Flask
from block_chain import BlockChain
from flask.json import jsonify
from flask.globals import request

## Initiation flash for API
## ---------------------------------------------------------------- ##
app = Flask(__name__)
node_identifier = str(uuid.uuid4()).replace('-', "") ## Indentifier for mining name
blockchain = BlockChain() ## Instanciate Blockchain

# Route
@app.route('/blockchain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

@app.route('/blockchain/mine', methods=['GET'])
def mine_block():
    blockchain.add_transaction(
        sender="0",
        recipient=node_identifier,
        amount_p=1
    )

    last_block_hash =  blockchain.hash_block(blockchain.last_block)
    indext = len(blockchain.chain)
    nonce = blockchain.proof_of_work(indext, last_block_hash, blockchain.current_transaction)
    block = blockchain.append_block(last_block_hash, nonce)
    response = {
        'message': "Block has been mined",
        'index': block['index'],
        'hash_of_previous_block': block['hash_of_previous_block'],
        'transaction': block['transaction'],
        'nonce': block['nonce']
    }

    return jsonify(response),200

@app.route('/transcation/new', methods=['POST'])
def new_transaction():
    value = request.get_json()

    replace_field = ['sender', 'recipient', 'amount']
    if not all(k in value for k in replace_field):
        return jsonify({'message': 'missing field'}), 404
    
    index = blockchain.add_transaction(
        value['sender'], value['amount'], value['recipient']
    )

    response = {
        'message': f'Transaction will be added to block {index}'
    }

    return jsonify(response),200

@app.route('/add/node', methods=['POST'])
def add_node():
    value = request.get_json()
    nodes = value['node']

    if nodes is None:
        return jsonify({
            'message': 'Missing Field Required'
        }),404
    
    blockchain.add_node(nodes)

    return jsonify({
        'message': 'Node was added',
        'node': nodes
    })

@app.route('/nodes', methods=['GET'])
def node():
    return jsonify({
        'node': list(blockchain.nodes)
    }), 200

@app.route('/sync/blockhain', methods=['GET'])
def sync():
    recent_update = blockchain.sync_node()
    if recent_update:
        return jsonify({
            'message': 'Node was updated'
        }), 201
    else:
        return jsonify({
            'message': 'Node was current update'
        }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(sys.argv[1]))