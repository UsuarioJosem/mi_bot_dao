from solcx import compile_standard, install_solc
from web3 import Web3
import json

# 1. Instalar compilador
install_solc("0.8.0")

# 2. Leer el contrato
with open("SimpleDAO.sol", "r") as file:
    source_code = file.read()

# 3. Compilar
compiled = compile_standard({
    "language": "Solidity",
    "sources": {
        "SimpleDAO.sol": {
            "content": source_code
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
            }
        }
    }
}, solc_version="0.8.0")

# 4. Guardar ABI y bytecode
bytecode = compiled["contracts"]["SimpleDAO.sol"]["SimpleDAO"]["evm"]["bytecode"]["object"]
abi = compiled["contracts"]["SimpleDAO.sol"]["SimpleDAO"]["abi"]

# 5. Conectar a Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
account = web3.eth.accounts[0]

# 6. Construir contrato
SimpleDAO = web3.eth.contract(abi=abi, bytecode=bytecode)

# 7. Crear transacción
nonce = web3.eth.get_transaction_count(account)
tx = SimpleDAO.constructor().build_transaction({
    "from": account,
    "nonce": nonce,
    "gas": 3000000,
    "maxFeePerGas": web3.to_wei("3", "gwei"),
    "maxPriorityFeePerGas": web3.to_wei("2", "gwei")
})

# 8. Firmar y enviar
signed_tx = web3.eth.account.sign_transaction(tx, import os
from dotenv import load_dotenv
load_dotenv()
private_key = os.getenv("PRIVATE_KEY")
tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

print("✅ Contrato desplegado en:", tx_receipt.contractAddress)
