import hashlib
import datetime
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder='.')


class Block:
    # Esta clase representa un bloque de la cadena de bloques
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index  # índice del bloque en la cadena
        self.timestamp = timestamp  # marca de tiempo
        self.data = data  # datos del bloque
        self.previous_hash = previous_hash  # hash del bloque anterior
        self.nonce = 0  # número de operaciones de prueba de trabajo
        self.hash = self.calculate_hash()  # hash del bloque actual

    def calculate_hash(self):
        # Calcula el hash del bloque
        sha = hashlib.sha256()  # crea un objeto hash
        # actualiza el hash con los datos del bloque
        sha.update(str(self.index).encode('utf-8') +
                   str(self.timestamp).encode('utf-8') +
                   str(self.data).encode('utf-8') +
                   str(self.previous_hash).encode('utf-8') +
                   str(self.nonce).encode('utf-8'))
        return sha.hexdigest()  # devuelve el hash en formato hexadecimal

    def mine_block(self, difficulty):
        # Realiza la minería del bloque y encuentra el hash correcto
        while self.hash[:difficulty] != "0" * difficulty:  # verifica si el hash del bloque comienza con ceros
            self.nonce += 1  # incrementa el nonce
            self.hash = self.calculate_hash()
        print("Block mined: " + self.hash)


class Blockchain:
    # clase que representa la cadena de bloques
    def __init__(self):
        self.chain = [self.create_genesis_block()]  # lista de bloques
        self.difficulty = 4  # dificultad para minar bloques
        self.pending_transactions = []  # transacciones pendientes

    def create_genesis_block(self):
        # crea el bloque génesis
        return Block(0, datetime.datetime.now(), "Genesis Block", "0")

    def get_latest_block(self):
        # devuelve el último bloque de la cadena
        return self.chain[-1]

    def add_block(self, new_block):
        # añade un nuevo bloque a la cadena
        new_block.previous_hash = self.get_latest_block().hash  # asigna el hash del último bloque como hash anterior
        new_block.mine_block(self.difficulty)  # mina el bloque
        self.chain.append(new_block)  # añade el bloque a la cadena

    def is_chain_valid(self):
        # verifica si la cadena de bloques es válida
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]  # bloque actual
            previous_block = self.chain[i - 1]  # bloque anterior

            # verifica si el hash del bloque actual es correcto
            if current_block.hash != current_block.calculate_hash():
                return False

            # verifica si el hash del bloque anterior es correcto
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def add_transaction(self, data):
        # añade una transacción pendiente a la lista
        self.pending_transactions.append(data)

    def mine_block(self):
        # mina un bloque con las transacciones pendientes
        new_block = Block(len(self.chain), datetime.datetime.now(), self.pending_transactions,
                          self.get_latest_block().hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = []  # vacía la lista de transacciones pendientes

    def get_block_by_index(self, index):
        # Obtiene un bloque por su índice
        if 0 <= index < len(self.chain):
            return self.chain[index]
        else:
            return None


blockchain = Blockchain()  # crea una cadena de bloques


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/blocks', methods=['GET'])
def get_blocks():
    blocks = []
    for block in blockchain.chain:
        blocks.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'data': block.data,
            'previous_hash': block.previous_hash,
            'hash': block.hash
        })
    return jsonify({'blocks': blocks})


@app.route('/block/<int:index>', methods=['GET'])
def get_block(index):
    block = blockchain.get_block_by_index(index)
    if block:
        block_info = {
            'index': block.index,
            'timestamp': block.timestamp,
            'data': block.data,
            'previous_hash': block.previous_hash,
            'hash': block.hash
        }
        return jsonify({'block': block_info})
    else:
        return jsonify({'message': 'Block not found'}), 404


@app.route('/mine_block', methods=['POST'])
def mine_block():
    data = request.get_json()
    new_block = Block(len(blockchain.chain), datetime.datetime.now(), data['data'], "")
    blockchain.add_block(new_block)
    return jsonify({'message': 'Block mined successfully'})


@app.route('/chain_status', methods=['GET'])
def chain_status():
    is_valid = blockchain.is_chain_valid()
    status_message = "Valid" if is_valid else "Invalid"
    return jsonify({'status': status_message})


@app.route('/send_transaction', methods=['POST'])
def send_transaction():
    data = request.get_json()
    blockchain.add_transaction(data['data'])
    return jsonify({'message': 'Transaction added to pending transactions'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
