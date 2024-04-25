import hashlib
import time
import json

# CREAR EL BLOQUE GENESIS
class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, nonce = 0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
    
    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
# CREAR LA CADENA DE BLOQUES
class Blockchain:
    def __init__(self):
        self.chain =  []
        self.create_genesis_block()
        
    def create_genesis_block(self):
        # creamos el primer bloque de manera manual
        genesis_block = Block(0, time.time(), [], "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
    
    # AGREGAMOS NUEVOS BLOQUES
    def add_block(self, block, proof):
        previous_hash = self.chain[-1].hash
        
        # Comprobamos si el hash anterior es igual al hash del último bloque
        if previous_hash != block.previous_hash:
            return False
        
        # Comprobamos si el bloque es válido
        if not Blockchain.is_valid_proof(block, proof):
            return False
        
        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, proof):
        # Comprobamos si el bloque empieza por '0000' (prueba de trabajo)
        return (proof.startswith('0000') and proof == block.compute_hash())
    
    # DEFINIR PRUEBA DE TRABAJO

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        
        #Incrementamos el nonce hasta que encontrar un hash válido 
        while not computed_hash.startswith('0000'):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash
    
# EJECUTAR EL PROGRAMA
# Creamos una instancia de la clase Blockchain
my_blockchain = Blockchain()

# Crear un nuevo bloque con algunas transacciones
new_block = Block(index = len(my_blockchain.chain),
                  timestamp = time.time(),
                  transactions = ["Transaccion 1", "Transaccion 2"],
                  previous_hash= my_blockchain.chain[-1].hash)

# Realizamos la prueba de trabajo
proof = my_blockchain.proof_of_work(new_block)

# Añadimos el bloque a la cadena
my_blockchain.add_block(new_block, proof)
                  