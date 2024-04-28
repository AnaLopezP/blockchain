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

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': str(self.timestamp),  # Convertir a cadena para serialización
            'data': self.data,
            'previous_hash': self.previous_hash,
            'hash': self.hash
        }
        
        
class Blockchain:
    # clase que representa la cadena de bloques
    def __init__(self):
        self.chain = [self.create_genesis_block()]  # lista de bloques
        self.difficulty = 4  # dificultad para minar bloques
        self.pending_transactions = []  # transacciones pendientes
        self.pending_diplomas = []
        
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

    
    def add_transaction(self, sender, recipient, message):
        #añade la transacción al bloque
        self.pending_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'message': message
        })

    def add_diploma(self, sender, recipient, diploma_name):
        #añade el diploma al bloque
        
        self.pending_diplomas.append({
            'sender': sender,
            'recipient': recipient,
            'diploma_name': diploma_name
        })

    def mine_pending_transactions(self):
        #se encarga de minar las transacciones pendientes
        if len(self.pending_transactions) > 0 or len(self.pending_diplomas) > 0: # Verifica si hay transacciones pendientes
            transaction_data = ', '.join([f"Sender: {tx['sender']} Recipient: {tx['recipient']} Message: {tx['message']}" for tx in self.pending_transactions]) # Concatena las transacciones pendientes
            diploma_data = ', '.join([f"Sender: {d['sender']} Name diploma: {d['diploma_name']} Recipient: {d['recipient']}" for d in self.pending_diplomas]) # Concatena los diplomas pendientes
            combined_data = f"Transactions: {transaction_data}, Diplomas: {diploma_data}" # Combina las transacciones y diplomas pendientes
            new_block = Block(len(self.chain), datetime.datetime.now(), combined_data, self.get_latest_block().hash) # Crea un nuevo bloque con las transacciones pendientes
            new_block.mine_block(self.difficulty) # Mina el bloque
            self.chain.append(new_block) # Añade el bloque a la cadena
            self.pending_transactions = [] # Limpia las transacciones pendientes
            self.pending_diplomas = [] # Limpia los diplomas pendientes


    def get_block_by_index(self, index):
        # Obtiene un bloque por su índice
        if 0 <= index < len(self.chain):
            return self.chain[index]
        else:
            return None


blockchain = Blockchain()  # crea una cadena de bloques

# Rutas de la API
@app.route('/') # Ruta para la página principal
def index():
    return render_template('index.html')


@app.route('/blocks', methods=['GET']) # Ruta para obtener todos los bloques
def get_blocks():
    # Obtiene todos los bloques de la cadena y los convierte a un diccionario
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


@app.route('/block/<int:index>', methods=['GET']) # Ruta para obtener un bloque por su índice
def get_block(index): 
    # Obtiene un bloque por su índice y lo convierte a un diccionario
    block = blockchain.get_block_by_index(index)
    if block:
        block_dict = block.to_dict() # Convierte el bloque a un diccionario
        print("Block dictionary:", block_dict)  # Imprimir el diccionario para depurar
        return jsonify({'block': block_dict})
    else:
        return jsonify({'message': 'Block not found'}), 404 # Devuelve un mensaje de error si no se encuentra el bloque


@app.route('/mine_block', methods=['POST']) # Ruta para minar un bloque
def mine_block():
    data = request.get_json() # Obtiene los datos del bloque a minar
    new_block = Block(len(blockchain.chain), datetime.datetime.now(), data['data'], "") # Crea un nuevo bloque
    blockchain.add_block(new_block) # Añade el bloque a la cadena
    return jsonify({'message': 'Block mined successfully'})


@app.route('/chain_status', methods=['GET']) # Ruta para verificar el estado de la cadena
def chain_status():
    is_valid = blockchain.is_chain_valid() # Verifica si la cadena es válida
    status_message = "Valid" if is_valid else "Invalid" # Mensaje de estado
    return jsonify({'status': status_message})



@app.route('/transaction_block', methods=['POST']) # Ruta para añadir una transacción al bloque
def transaction_block():
    data = request.get_json() # Obtiene los datos de la transacción
    sender = data.get('sender') # Obtiene el remitente
    recipient = data.get('recipient') # Obtiene el destinatario
    message = data.get('message') # Obtiene el mensaje
    if sender is None or recipient is None or message is None: # Verifica
        return jsonify({'message': 'Invalid transaction data'}), 400

    blockchain.add_transaction(sender, recipient, message) # Añade la transacción al bloque
    blockchain.mine_pending_transactions()  # Llama al método para minar bloques pendientes
    return jsonify({'message': 'Transaction added successfully and block mined'}), 201


@app.route('/mine_pending_transactions', methods=['GET']) # Ruta para minar las transacciones pendientes
def mine_pending_transactions():
    blockchain.mine_pending_transactions() # Llama al método para minar bloques pendientes
    return jsonify({'message': 'Pending transactions mined successfully'})

@app.route('/diplom_block', methods=['POST']) # Ruta para añadir un diploma al bloque
def diplom_block():
    data = request.get_json() # Obtiene los datos del diploma
    sender = data.get('sender') # Obtiene el remitente
    recipient = data.get('recipient') # Obtiene el destinatario
    diploma_name = data.get('diploma_name') # Obtiene el nombre del diploma
    if sender is None or recipient is None or diploma_name is None: # Verifica
        return jsonify({'message': 'Invalid diploma data'}), 400

    blockchain.add_diploma(sender, recipient, diploma_name) # Añade el diploma al bloque
    blockchain.mine_pending_transactions()  # Llama al método para minar bloques pendientes
    return jsonify({'message': 'Diploma added successfully and block mined'}), 201


if __name__ == '__main__':
    app.run(debug=True, port=5000)


