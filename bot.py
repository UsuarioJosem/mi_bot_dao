import requests
import pandas as pd
from datetime import datetime
import os
import schedule
import time
from web3 import Web3
import json
from solcx import compile_standard, install_solc

# ------------------------ PRECIOS ------------------------
def recolectar_datos():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    respuesta = requests.get(url)
    return respuesta.json()

def obtener_historial(crypto_id="bitcoin", dias=7):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={dias}"
    respuesta = requests.get(url)
    datos = respuesta.json()
    return [p[1] for p in datos["prices"]]

def calcular_sma(lista_precios):
    return sum(lista_precios) / len(lista_precios)

# --------------------- ANÁLISIS --------------------------
def analizar(precios):
    historial_btc = obtener_historial("bitcoin")
    historial_eth = obtener_historial("ethereum")

    sma_btc_r, sma_btc_l = calcular_smas(historial_btc)
    sma_eth_r, sma_eth_l = calcular_smas(historial_eth)

    mensajes = []

    if sma_btc_r > sma_btc_l and btc_actual > sma_btc_r:
        mensajes.append("📈 BTC señal de compra (cruce dorado + confirmación)")
    elif sma_btc_r < sma_btc_l:
        mensajes.append("⚠️ BTC señal de venta (cruce de la muerte)")

    if sma_eth_r > sma_eth_l and eth_actual > sma_eth_r:
        mensajes.append("📈 ETH señal de compra (cruce dorado + confirmación)")
    elif sma_eth_r < sma_eth_l:
        mensajes.append("⚠️ ETH señal de venta (cruce de la muerte)")

    if not mensajes:
        return "Mercado estable"
    return " | ".join(mensajes)

# -------------------- CSV HISTORIAL ----------------------
def archivo_existe():
    return os.path.isfile("historial_bot.csv")

def registrar_decision(precios, decision)
    if "compra" in decision.lower() or "venta" in decision.lower():
        simular_inversion(decision):
    fila = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "precio_btc": precios["bitcoin"]["usd"],
        "precio_eth": precios["ethereum"]["usd"],
        "decision": decision
    }
    df = pd.DataFrame([fila])
    df.to_csv("historial_bot.csv", mode="a", index=False, header=not archivo_existe())

# ---------------------- DAO ------------------------------
def enviar_propuesta_dao(mensaje):
    print("🧠 Enviando propuesta a la DAO...")

    contract_address = Web3.to_checksum_address("0xD6C7155dD58b50752F692Cf6CE94663801bF77e2")
    from dotenv import load_dotenv
    import os
    load_dotenv()
    private_key = os.getenv("PRIVATE_KEY")
    web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
    account = web3.eth.accounts[0]

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

    proposal_id = contract.functions.getProposalCount().call()

    nonce = web3.eth.get_transaction_count(account)
    tx = contract.functions.createProposal(mensaje).build_transaction({
        "from": account,
        "nonce": nonce,
        "gas": 2000000,
        "maxFeePerGas": web3.to_wei("3", "gwei"),
        "maxPriorityFeePerGas": web3.to_wei("2", "gwei")
    })

    signed = web3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    web3.eth.wait_for_transaction_receipt(tx_hash)
    print("✅ Propuesta creada en la DAO. ID:", proposal_id)
    return proposal_id, contract, account, private_key, web3

def votar_automaticamente(proposal_id, contract, account, private_key, web3):
    print("🗳️ Votando a favor de la propuesta...")
    nonce = web3.eth.get_transaction_count(account)
    tx = contract.functions.vote(proposal_id, True).build_transaction({
        "from": account,
        "nonce": nonce,
        "gas": 2000000,
        "maxFeePerGas": web3.to_wei("3", "gwei"),
        "maxPriorityFeePerGas": web3.to_wei("2", "gwei")
    })

    signed = web3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    web3.eth.wait_for_transaction_receipt(tx_hash)
    print("✅ Voto registrado en la DAO.")

# --------------------- CICLO BOT -------------------------
def ciclo():
    try:
        precios = recolectar_datos()
        print("Precios actuales:", precios)

        decision = analizar(precios)
        print("Decisión del bot:", decision)

        registrar_decision(precios, decision)
    if "compra" in decision.lower() or "venta" in decision.lower():
        simular_inversion(decision)

        if "compra" in decision.lower():
            proposal_id, contract, account, private_key, web3 = enviar_propuesta_dao(decision)
            votar_automaticamente(proposal_id, contract, account, private_key, web3)
            ejecutar_propuestas_pendientes(contract, account, private_key, web3)

        print("Ciclo completado.\n")

    except Exception as e:
        print("❌ Error en el ciclo:", e)

# ---------------------- AUTOMATIZACIÓN -------------------
schedule.every(60).minutes.do(ciclo)
print("🤖 Bot ejecutándose cada 60 minutos. Presiona Ctrl+C para detener.")
ciclo()  # Ejecuta una vez ahora

def ejecutar_propuestas_pendientes(contract, account, private_key, web3):
    total = contract.functions.getProposalCount().call()

    for i in range(total):
        descripcion, votos_si, votos_no, ejecutada = contract.functions.getProposal(i).call()

        if not ejecutada and votos_si > votos_no:
            print(f"🚀 Ejecutando propuesta {i}: {descripcion}")
            nonce = web3.eth.get_transaction_count(account)
            tx = contract.functions.execute(i).build_transaction({
                "from": account,
                "nonce": nonce,
                "gas": 2000000,
                "maxFeePerGas": web3.to_wei("3", "gwei"),
                "maxPriorityFeePerGas": web3.to_wei("2", "gwei")
            })

            signed = web3.eth.account.sign_transaction(tx, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"✅ Propuesta {i} ejecutada. Tx Hash: {tx_hash.hex()}")

while True:
    schedule.run_pending()
    time.sleep(1)

def calcular_smas(lista_precios):
    sma_rapida = sum(lista_precios[-3:]) / 3
    sma_lenta = sum(lista_precios) / len(lista_precios)
    return sma_rapida, sma_lenta

def simular_inversion(decision):
    with open("fondos_virtuales.log", "a") as f:
        f.write(f"{datetime.now()} → {decision}\n")
