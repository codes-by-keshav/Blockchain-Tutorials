import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain :
    def __init__(self) :
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, prvs_hash='0')
        self.nodes = set()

    def create_block(self,proof,prvs_hash) :
        block = {
            'index' : len(self.chain)+1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prvs_hash': prvs_hash,
            'transactions': self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_prvs_block(self):
        return self.chain[-1] # returns the last block in the chain
    
    def proof_of_work(self, prvs_proof) :
        new_proof = 1
        check_proof = False
        while check_proof is False :
            hash_operation = hashlib.sha256(str(new_proof**2 - prvs_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000' :
                check_proof = True
            else :
                new_proof += 1
        return new_proof
       
    def hash(self, block) :
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain) :
        prvs_block = chain[0]
        block_index = 1
        while block_index < len(chain) :
            block = chain[block_index]
            if block['prvs_hash'] != self.hash(prvs_block) :
                return False
            prvs_proof = prvs_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - prvs_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000' :
                return False
            prvs_block = block
            block_index += 1
        return True
    
    def get_nodes(self):
        return list(self.nodes)
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        prvs_block = self.get_prvs_block()
        return prvs_block['index'] + 1
    
    def add_node(self,address):
        parsed_url= urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    
app = Flask(__name__)

node_address = str(uuid4()).replace('-', '')

myblockchain=Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    prvs_block = myblockchain.get_prvs_block()
    prvs_proof = prvs_block['proof']
    proof = myblockchain.proof_of_work(prvs_proof)
    prvs_hash = myblockchain.hash(prvs_block)
    myblockchain.add_transaction(sender=node_address, receiver='Keshav_ka_beta', amount=10)
    block = myblockchain.create_block(proof, prvs_hash)
    current_block_hash = myblockchain.hash(block)
    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'prvs_hash': block['prvs_hash'],
        'current_hash' : current_block_hash,
        'transactions': block['transactions']
    }
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    # chain_with_hashes = []
    # for block in myblockchain.chain:
    #     block_with_hash = block.copy()
    #     block_with_hash['current_hash'] = myblockchain.hash(block)
    #     chain_with_hashes.append(block_with_hash)
    
    # response = {
    #     'chain': chain_with_hashes,
    #     'length': len(myblockchain.chain)
    # }
    # return jsonify(response), 200
    response = {'chain': myblockchain.chain,
                'length': len(myblockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = myblockchain.is_chain_valid(myblockchain.chain)
    if is_valid:
        response = {
            'message': 'The blockchain is valid.'
        }
    else:
        response = {
            'message': 'The blockchain is not valid.'
        }
    return jsonify(response), 200

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = myblockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node', 400
    for node in nodes:
        myblockchain.add_node(node)
    response = {
        'message': 'All the nodes are now connected. The MyCoin Blockchain now contains the following nodes:',
        'total_nodes': list(myblockchain.nodes)
    }
    return jsonify(response), 201

@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = myblockchain.replace_chain()
    if is_chain_replaced:
        response = {
            'message': 'The nodes had different chains so the chain was replaced by the longest one.',
            'new_chain': myblockchain.chain
        }
    else:
        response = {
            'message': 'All good. The chain is the largest one.',
            'actual_chain': myblockchain.chain
        }
    return jsonify(response), 200

@app.route('/get_nodes', methods=['GET'])
def get_nodes():
    nodes = myblockchain.get_nodes()
    response = {
        'nodes': nodes,
        'total_nodes': len(nodes)
    }
    return jsonify(response), 200




app.run(host='0.0.0.0', port=5002)
