import datetime
import hashlib
import json
from flask import Flask, jsonify

class Blockchain :
    def __init__(self) :
        self.chain = []
        self.create_block(proof=1, prvs_hash='0')

    def create_block(self,proof,prvs_hash) :
        block = {
            'index' : len(self.chain)+1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prvs_hash': prvs_hash
        }
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
    
app = Flask(__name__)

myblockchain=Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    prvs_block = myblockchain.get_prvs_block()
    prvs_proof = prvs_block['proof']
    proof = myblockchain.proof_of_work(prvs_proof)
    prvs_hash = myblockchain.hash(prvs_block)
    block = myblockchain.create_block(proof, prvs_hash)
    current_block_hash = myblockchain.hash(block)
    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'prvs_hash': block['prvs_hash'],
        'current_hash' : current_block_hash
    }
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    chain_with_hashes = []
    for block in myblockchain.chain:
        block_with_hash = block.copy()
        block_with_hash['current_hash'] = myblockchain.hash(block)
        chain_with_hashes.append(block_with_hash)
    
    response = {
        'chain': chain_with_hashes,
        'length': len(myblockchain.chain)
    }
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

app.run(host='0.0.0.0', port=5000)
