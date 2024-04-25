import hashlib
import datetime

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.nonce = 0

    def calculate_hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.index).encode('utf-8') +
                  str(self.timestamp).encode('utf-8') +
                  str(self.data).encode('utf-8') +
                  str(self.previous_hash).encode('utf-8') +
                  str(self.nonce).encode('utf-8'))
        return sha.hexdigest()
    
    def mine_block(self, difficulty):
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print("Block mined: " + self.hash)

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4

    def create_genesis_block(self):
        return Block(0, datetime.datetime.now(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True
    
#ejemplo
if __name__ == '__main__':
    blockchain = Blockchain()
    print("Mining block 1...")
    blockchain.add_block(Block(1, datetime.datetime.now(), "Amount: 4", ""))
    print("Mining block 2...")
    blockchain.add_block(Block(2, datetime.datetime.now(), "Amount: 10", ""))
    print('Es la cadena valida?:', blockchain.is_chain_valid())
