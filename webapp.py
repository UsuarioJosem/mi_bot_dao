from flask import Flask, render_template, request, redirect
from web3 import Web3
from solcx import compile_standard, install_solc

app = Flask(__name__)

# Conexión Web3
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract_address = Web3.to_checksum_address("0xD6C7155dD58b50752F692Cf6CE94663801bF77e2")  # tu contrato
import os
from dotenv import load_dotenv
load_dotenv()
private_key = os.getenv("PRIVATE_KEY")
account = web3.eth.accounts[0]

# Compilar contrato
with open("SimpleDAO.sol", "r") as f:
    source_code = f.read()

install_solc("0.8.0")
compiled = compile_standard({
    "language": "Solidity",
    "sources": {"SimpleDAO.sol": {"content": source_code}},
    "settings": {"outputSelection": {"*": {"*": ["abi"]}}}
}, solc_version="0.8.0")

abi = compiled["contracts"]["SimpleDAO.sol"]["SimpleDAO"]["abi"]
contract = web3.eth.contract(address=contract_address, abi=abi)

@app.route("/", methods=["GET"])
def home():
    propuestas = []
    total = contract.functions.getProposalCount().call()

    for i in range(total):
        descripcion, votos_si, votos_no, ejecutada = contract.functions.getProposal(i).call()
        propuestas.append({
            "id": i,
            "descripcion": descripcion,
            "votos_si": votos_si,
            "votos_no": votos_no,
            "ejecutada": "✅" if ejecutada else "❌"
        })

    return render_template("index.html", propuestas=propuestas)

@app.route("/votar/<int:proposal_id>", methods=["POST"])
def votar(proposal_id):
    nonce = web3.eth.get_transaction_count(account)
    tx = contract.functions.vote(proposal_id, True).build_transaction({
        "from": account,
        "nonce": nonce,
        "gas": 2000000,
        "maxFeePerGas": web3.to_wei("3", "gwei"),
        "maxPriorityFeePerGas": web3.to_wei("2", "gwei")
    })
    signed = web3.eth.account.sign_transaction(tx, private_key=private_key)
    web3.eth.send_raw_transaction(signed.raw_transaction)
    return redirect("/")

@app.route("/ejecutar/<int:proposal_id>", methods=["POST"])
def ejecutar(proposal_id):
    nonce = web3.eth.get_transaction_count(account)
    tx = contract.functions.execute(proposal_id).build_transaction({
        "from": account,
        "nonce": nonce,
        "gas": 2000000,
        "maxFeePerGas": web3.to_wei("3", "gwei"),
        "maxPriorityFeePerGas": web3.to_wei("2", "gwei")
    })
    signed = web3.eth.account.sign_transaction(tx, private_key=private_key)
    web3.eth.send_raw_transaction(signed.raw_transaction)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
