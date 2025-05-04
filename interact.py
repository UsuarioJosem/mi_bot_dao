from web3 import Web3
import json

# 1. Conectar a Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# 2. Dirección del contrato desplegado
contract_address = Web3.to_checksum_address("0xD6C7155dD58b50752F692Cf6CE94663801bF77e2")

# 3. Cuenta y clave privada
account = web3.eth.accounts[0]
import os
from dotenv import load_dotenv
load_dotenv()
private_key = os.getenv("PRIVATE_KEY")

# 4. Cargar ABI (desde deploy.py o JSON guardado)
with open("SimpleDAO.sol", "r") as file:
    source_code = file.read()

from solcx import compile_standard, install_solc
install_solc("0.8.0")

compiled = compile_standard({
    "language": "Solidity",
    "sources": {"SimpleDAO.sol": {"content": source_code}},
    "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
}, solc_version="0.8.0")

abi = compiled["contracts"]["SimpleDAO.sol"]["SimpleDAO"]["abi"]

# 5. Cargar contrato
contract = web3.eth.contract(address=contract_address, abi=abi)

# ✅ Función: crear propuesta
def crear_propuesta(texto):
    nonce = web3.eth.get_transaction_count(account)
    tx = contract.functions.createProposal(texto).build_transaction({
        "from": account,
        "nonce": nonce,
        "gas": 2000000,
        "maxFeePerGas": web3.to_wei("3", "gwei"),
        "maxPriorityFeePerGas": web3.to_wei("2", "gwei")
    })

    signed = web3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print("✅ Propuesta creada. Hash:", tx_hash.hex())

# ✅ Función: leer propuesta
def ver_propuesta(id):
    propuesta = contract.functions.getProposal(id).call()
    print(f"📋 Propuesta {id}:\nDescripción: {propuesta[0]}\nSí: {propuesta[1]}\nNo: {propuesta[2]}\nEjecutada: {propuesta[3]}")

# ✅ Función: votar
def votar(id, a_favor=True):
    nonce = web3.eth.get_transaction_count(account)
    tx = contract.functions.vote(id, a_favor).build_transaction({
        "from": account,
        "nonce": nonce,
        "gas": 2000000,
        "maxFeePerGas": web3.to_wei("3", "gwei"),
        "maxPriorityFeePerGas": web3.to_wei("2", "gwei")
    })

    signed = web3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print("🗳️ Voto enviado. Hash:", tx_hash.hex())

# ✅ Función: ejecutar propuesta
def ejecutar(id):
    nonce = web3.eth.get_transaction_count(account)
    tx = contract.functions.execute(id).build_transaction({
        "from": account,
        "nonce": nonce,
        "gas": 2000000,
        "maxFeePerGas": web3.to_wei("3", "gwei"),
        "maxPriorityFeePerGas": web3.to_wei("2", "gwei")
    })

    signed = web3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print("🚀 Propuesta ejecutada. Hash:", tx_hash.hex())

# 🔁 Ejemplo de uso:
crear_propuesta("Comprar ETH para el fondo común")
ver_propuesta(0)
votar(0, True)
ejecutar(0)
