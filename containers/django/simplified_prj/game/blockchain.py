# blockchain.py
from django.conf import settings
from web3 import Web3
from eth_account import Account

# Connect to your blockchain node
web3 = Web3(Web3.HTTPProvider(settings.SEPOLIA_URL))

# Define your smart contract (replace with your actual contract address and ABI)
contract_address = settings.CONTRACT_ADDRESS
contract_abi = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            }
        ],
        "name": "OwnableInvalidOwner",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            }
        ],
        "name": "OwnableUnauthorizedAccount",
        "type": "error"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "string",
                "name": "player1",
                "type": "string"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "player2",
                "type": "string"
            },
            {
                "indexed": False,
                "internalType": "uint8",
                "name": "player1Score",
                "type": "uint8"
            },
            {
                "indexed": False,
                "internalType": "uint8",
                "name": "player2Score",
                "type": "uint8"
            }
        ],
        "name": "GameSaved",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "previousOwner",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "newOwner",
                "type": "address"
            }
        ],
        "name": "OwnershipTransferred",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "counter",
        "outputs": [
            {
                "type": "constructor",
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "name": "games",
        "outputs": [
            {
                "internalType": "string",
                "name": "player1",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "player2",
                "type": "string"
            },
            {
                "internalType": "uint8",
                "name": "player1Score",
                "type": "uint8"
            },
            {
                "internalType": "uint8",
                "name": "player2Score",
                "type": "uint8"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "renounceOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_player1",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "_player2",
                "type": "string"
            },
            {
                "internalType": "uint8",
                "name": "_player1Score",
                "type": "uint8"
            },
            {
                "internalType": "uint8",
                "name": "_player2Score",
                "type": "uint8"
            }
        ],
        "name": "saveGameScore",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "newOwner",
                "type": "address"
            }
        ],
        "name": "transferOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]  # Your contract ABI here

private_key = settings.PRIVATE_KEY
account = Account.from_key(private_key)
# web3.eth.defaultAccount = account.address
# web3.eth.account.add(account)
contract = web3.eth.contract(address=contract_address, abi=contract_abi)


def save_game_score_(player1_username, player2_username, player1_score, player2_score):
    nonce = web3.eth.get_transaction_count(account.address, 'pending')
    transaction = (contract.functions.saveGameScore(player1_username, player2_username, player1_score, player2_score)
                   .build_transaction({'from': account.address,
                                       'nonce': nonce}))
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=account.key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt:
        response = ({
            'status': 'success',
            'receipt': {
                'transactionHash': receipt['transactionHash'].hex(),
                'blockHash': receipt['blockHash'].hex(),
                'blockNumber': receipt['blockNumber'],
                'gasUsed': receipt['gasUsed'],
                'status': receipt['status']
            }
        })
    else:
        response = ({'status': 'error', 'message': 'Failed to save game score'})
    return response
