from web3 import Web3
import requests
from config import *
import multiprocessing

def get_claimable_tokens(address, w3):
    contract_address = w3.to_checksum_address(CLAIM_ADDRESS)
    contract_data = w3.eth.contract(address=contract_address, abi=CLAIM_ABI)
    claimable_balance = contract_data.functions.claimableTokens(address).call()
    return claimable_balance

def inch_approve(data):
    private_key = data.split(';')[0]
    if RPC_URL == '':
        _RPC_URL = data.split(';')[2]
    else:
        _RPC_URL = RPC_URL
    w3 = Web3(Web3.HTTPProvider(_RPC_URL))
    account = w3.eth.account.from_key(private_key)
    address = account.address
    print(f'{address} | Делаю апрув ARB')
    try:
        amount_to_approve = get_claimable_tokens(address, w3)
        #amount_to_approve = 100000000000000000000000
        inchurl = f'https://api.1inch.io/v4.0/42161/approve/transaction?tokenAddress={ARB_ADDRESS}&amount={amount_to_approve}'
        json_data = requests.get(inchurl)
        api_data = json_data.json()
        nonce = w3.eth.get_transaction_count(address)
        transaction = {
            "nonce": nonce,
            "to": w3.to_checksum_address(api_data["to"]),
            "data": api_data["data"],
            "gasPrice": w3.eth.gas_price,
            "gas": 2000000
        }

        sign_transaction = account.sign_transaction(transaction)
        transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)

        print(f'{address} | Апрув успешно прошёл: {SCAN}/{w3.to_hex(transaction_hash)}')
    except Exception as e:
        print(f'{address} | Ошибка апрува: {e}')

if __name__ == "__main__":
    with open('data.txt', 'r') as f:
        data = f.read().splitlines()

    with multiprocessing.Pool(multiprocessing.cpu_count() * 3) as p:
        p.map(inch_approve, data)
        p.join()
        print('Апрув "ARB" для всех аккаунтов завершён!')