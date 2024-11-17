import json
from swarm import Agent
from cdp import *
from typing import List, Dict, Any
import os
from openai import OpenAI
from decimal import Decimal
from typing import Union
from web3 import Web3
import web3
from web3.exceptions import ContractLogicError
from cdp.errors import ApiError, UnsupportedAssetError
from web3.auto import w3
from datetime import datetime, timedelta
import requests

# Get configuration from environment variables
API_KEY_NAME = os.environ.get("CDP_API_KEY_NAME")
PRIVATE_KEY = os.environ.get("CDP_PRIVATE_KEY", "").replace('\\n', '\n')

# Configure CDP with environment variables
Cdp.configure(API_KEY_NAME, PRIVATE_KEY)

# Create a new wallet on the Base Sepolia testnet
# You could make this a function for the agent to create a wallet on any network
# If you want to use Base Mainnet, change Wallet.create() to Wallet.create(network_id="base-mainnet")
# see https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets for more information
# agent_wallet = Wallet.create(network_id="base-mainnet")

# NOTE: the wallet is not currently persisted, meaning that it will be deleted after the agent is stopped. To persist the wallet, see https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets#developer-managed-wallets
# Here's an example of how to persist the wallet:
# WARNING: This is for development only - implement secure storage in production!

# # Export wallet data (contains seed and wallet ID)
# wallet_data = agent_wallet.export_data()
# wallet_dict = wallet_data.to_dict()

# # Example of saving to encrypted local file
# file_path = "wallet_seed.json"
# agent_wallet.save_seed(file_path, encrypt=True)
# print(f"Seed for wallet {agent_wallet.id} saved to {file_path}")

# # Example of loading a saved wallet:
# # 1. Fetch the wallet by ID
fetched_wallet = Wallet.fetch("4da29ae1-c62c-4833-b706-b71182794476")

# # 2. Load the saved seed
fetched_wallet.load_seed("wallet_seed.json")
wallet_data = fetched_wallet.export_data()
# Example of importing previously exported wallet data:
agent_wallet = Wallet.import_data(wallet_data)

# Request funds from the faucet (only works on testnet)
#faucet = agent_wallet.faucet()fetched_wallet = Wallet.fetch("4da29ae1-c62c-4833-b706-b71182794476")
if fetched_wallet is not None:
    wallet_data = fetched_wallet.export_data()
    print(f"Agen t wallet address:                                         {agent_wallet.default_address.address_id}")
else:
    print("Wallet not found.")
#print(f"Faucet transaction: {faucet}")

# wallet_dict = wallet_data.to_dict()
infura_url = 'https://base-rpc.publicnode.com'
web3 = Web3(Web3.HTTPProvider(infura_url))

portfolio_abi = [{
    "inputs": [],
    "stateMutability": "nonpayable",
    "type": "constructor"
}, {
    "inputs": [],
    "name": "CallerNotSuperAdmin",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidAddress",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidThresholdLength",
    "type": "error"
}, {
    "inputs": [],
    "name": "ModuleNotInitialised",
    "type": "error"
}, {
    "inputs": [],
    "name": "NoOwnerPassed",
    "type": "error"
}, {
    "inputs": [],
    "name": "PortfolioCreationIsPause",
    "type": "error"
}, {
    "inputs": [],
    "name": "ProtocolIsPaused",
    "type": "error"
}, {
    "inputs": [],
    "name": "ProtocolNotPaused",
    "type": "error"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": False,
        "internalType": "address",
        "name": "previousAdmin",
        "type": "address"
    }, {
        "indexed": False,
        "internalType": "address",
        "name": "newAdmin",
        "type": "address"
    }],
    "name":
    "AdminChanged",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "beacon",
        "type": "address"
    }],
    "name":
    "BeaconUpgraded",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": False,
        "internalType": "uint8",
        "name": "version",
        "type": "uint8"
    }],
    "name":
    "Initialized",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
    }],
    "name":
    "OwnershipTransferStarted",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
    }],
    "name":
    "OwnershipTransferred",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "bool",
        "name": "state",
        "type": "bool"
    }],
    "name":
    "PortfolioCreationState",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "components": [{
            "internalType": "address",
            "name": "portfolio",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "tokenExclusionManager",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "rebalancing",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "owner",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "assetManagementConfig",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "feeModule",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "vaultAddress",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "gnosisModule",
            "type": "address"
        }],
        "indexed":
        False,
        "internalType":
        "struct PortfolioFactory.PortfoliolInfo",
        "name":
        "portfolioData",
        "type":
        "tuple"
    }, {
        "indexed": True,
        "internalType": "uint256",
        "name": "portfolioId",
        "type": "uint256"
    }, {
        "indexed": False,
        "internalType": "string",
        "name": "_name",
        "type": "string"
    }, {
        "indexed": False,
        "internalType": "string",
        "name": "_symbol",
        "type": "string"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "_owner",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "_accessController",
        "type": "address"
    }, {
        "indexed": False,
        "internalType": "bool",
        "name": "isPublicPortfolio",
        "type": "bool"
    }],
    "name":
    "PortfolioInfo",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
    }],
    "name":
    "TransferSuperAdminOwnership",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "newImplementation",
        "type": "address"
    }],
    "name":
    "UpdataTokenRemovalVaultBaseAddress",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "newGnosisSingleton",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "newGnosisFallbackLibrary",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "newGnosisMultisendLibrary",
        "type": "address"
    }, {
        "indexed": False,
        "internalType": "address",
        "name": "newGnosisSafeProxyFactory",
        "type": "address"
    }],
    "name":
    "UpdateGnosisAddresses",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "newImplementation",
        "type": "address"
    }],
    "name":
    "UpgradeAssetManagerConfig",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "newImplementation",
        "type": "address"
    }],
    "name":
    "UpgradeFeeModule",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "newImplementation",
        "type": "address"
    }],
    "name":
    "UpgradePortfolio",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "newImplementation",
        "type": "address"
    }],
    "name":
    "UpgradeRebalance",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "newImplementation",
        "type": "address"
    }],
    "name":
    "UpgradeTokenExclusionManager",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "implementation",
        "type": "address"
    }],
    "name":
    "Upgraded",
    "type":
    "event"
}, {
    "inputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "name":
    "PortfolioInfolList",
    "outputs": [{
        "internalType": "address",
        "name": "portfolio",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "tokenExclusionManager",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "rebalancing",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "owner",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "assetManagementConfig",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "feeModule",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "vaultAddress",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "gnosisModule",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name": "acceptOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "inputs": [{
        "components": [{
            "internalType": "address",
            "name": "_assetManagerTreasury",
            "type": "address"
        }, {
            "internalType": "address[]",
            "name": "_whitelistedTokens",
            "type": "address[]"
        }, {
            "internalType": "uint256",
            "name": "_managementFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_performanceFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_entryFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_exitFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_initialPortfolioAmount",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_minPortfolioTokenHoldingAmount",
            "type": "uint256"
        }, {
            "internalType": "bool",
            "name": "_public",
            "type": "bool"
        }, {
            "internalType": "bool",
            "name": "_transferable",
            "type": "bool"
        }, {
            "internalType": "bool",
            "name": "_transferableToPublic",
            "type": "bool"
        }, {
            "internalType": "bool",
            "name": "_whitelistTokens",
            "type": "bool"
        }, {
            "internalType": "string",
            "name": "_name",
            "type": "string"
        }, {
            "internalType": "string",
            "name": "_symbol",
            "type": "string"
        }],
        "internalType":
        "struct FunctionParameters.PortfolioCreationInitData",
        "name":
        "initData",
        "type":
        "tuple"
    }, {
        "internalType": "address[]",
        "name": "_owners",
        "type": "address[]"
    }, {
        "internalType": "uint256",
        "name": "_threshold",
        "type": "uint256"
    }],
    "name":
    "createPortfolioCustodial",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "components": [{
            "internalType": "address",
            "name": "_assetManagerTreasury",
            "type": "address"
        }, {
            "internalType": "address[]",
            "name": "_whitelistedTokens",
            "type": "address[]"
        }, {
            "internalType": "uint256",
            "name": "_managementFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_performanceFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_entryFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_exitFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_initialPortfolioAmount",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_minPortfolioTokenHoldingAmount",
            "type": "uint256"
        }, {
            "internalType": "bool",
            "name": "_public",
            "type": "bool"
        }, {
            "internalType": "bool",
            "name": "_transferable",
            "type": "bool"
        }, {
            "internalType": "bool",
            "name": "_transferableToPublic",
            "type": "bool"
        }, {
            "internalType": "bool",
            "name": "_whitelistTokens",
            "type": "bool"
        }, {
            "internalType": "string",
            "name": "_name",
            "type": "string"
        }, {
            "internalType": "string",
            "name": "_symbol",
            "type": "string"
        }],
        "internalType":
        "struct FunctionParameters.PortfolioCreationInitData",
        "name":
        "initData",
        "type":
        "tuple"
    }],
    "name":
    "createPortfolioNonCustodial",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "uint256",
        "name": "portfoliofundId",
        "type": "uint256"
    }],
    "name":
    "getPortfolioList",
    "outputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "gnosisFallbackLibrary",
    "outputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "gnosisMultisendLibrary",
    "outputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "gnosisSafeProxyFactory",
    "outputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "gnosisSingleton",
    "outputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "components": [{
            "internalType": "address",
            "name": "_basePortfolioAddress",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_baseTokenExclusionManagerAddress",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_baseRebalancingAddres",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_baseAssetManagementConfigAddress",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_feeModuleImplementationAddress",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_baseTokenRemovalVaultImplementation",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_baseVelvetGnosisSafeModuleAddress",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_gnosisSingleton",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_gnosisFallbackLibrary",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_gnosisMultisendLibrary",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_gnosisSafeProxyFactory",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_protocolConfig",
            "type": "address"
        }],
        "internalType":
        "struct FunctionParameters.PortfolioFactoryInitData",
        "name":
        "initData",
        "type":
        "tuple"
    }],
    "name":
    "initialize",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function",
}]

fund_abi = [{
    "inputs": [],
    "stateMutability": "nonpayable",
    "type": "constructor"
}, {
    "inputs": [],
    "name": "AlreadyInitialized",
    "type": "error"
}, {
    "inputs": [],
    "name": "AmountCannotBeZero",
    "type": "error"
}, {
    "inputs": [],
    "name": "BalanceOfVaultIsZero",
    "type": "error"
}, {
    "inputs": [],
    "name": "CallerNeedToMaintainMinTokenAmount",
    "type": "error"
}, {
    "inputs": [],
    "name": "CallerNotHavingGivenPortfolioTokenAmount",
    "type": "error"
}, {
    "inputs": [],
    "name": "CallerNotPortfolioManager",
    "type": "error"
}, {
    "inputs": [],
    "name": "CallerNotRebalancerContract",
    "type": "error"
}, {
    "inputs": [],
    "name": "CallerNotSuperAdmin",
    "type": "error"
}, {
    "inputs": [],
    "name": "ClaimFailed",
    "type": "error"
}, {
    "inputs": [],
    "name": "CoolDownPeriodNotPassed",
    "type": "error"
}, {
    "inputs": [],
    "name": "DivisionByZero",
    "type": "error"
}, {
    "inputs": [],
    "name": "InsufficientAllowance",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidAddress",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidCastToUint160",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidDepositInputLength",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidExemptionTokens",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidExemptionTokensLength",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidMintAmount",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidSpender",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidTokenAddress",
    "type": "error"
}, {
    "inputs": [],
    "name": "MintedAmountIsNotAccepted",
    "type": "error"
}, {
    "inputs": [],
    "name": "PortfolioTokenNotInitialized",
    "type": "error"
}, {
    "inputs": [],
    "name": "ProtocolIsPaused",
    "type": "error"
}, {
    "inputs": [],
    "name": "TokenAlreadyExist",
    "type": "error"
}, {
    "inputs": [{
        "internalType": "uint256",
        "name": "limit",
        "type": "uint256"
    }],
    "name":
    "TokenCountOutOfLimit",
    "type":
    "error"
}, {
    "inputs": [],
    "name": "TokenNotEnabled",
    "type": "error"
}, {
    "inputs": [],
    "name": "TokenNotWhitelisted",
    "type": "error"
}, {
    "inputs": [],
    "name": "TransferFailed",
    "type": "error"
}, {
    "inputs": [],
    "name": "Transferprohibited",
    "type": "error"
}, {
    "inputs": [],
    "name": "UserNotAllowedToDeposit",
    "type": "error"
}, {
    "inputs": [],
    "name": "WithdrawalAmountIsSmall",
    "type": "error"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": False,
        "internalType": "address",
        "name": "previousAdmin",
        "type": "address"
    }, {
        "indexed": False,
        "internalType": "address",
        "name": "newAdmin",
        "type": "address"
    }],
    "name":
    "AdminChanged",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "owner",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "spender",
        "type": "address"
    }, {
        "indexed": False,
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
    }],
    "name":
    "Approval",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "beacon",
        "type": "address"
    }],
    "name":
    "BeaconUpgraded",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "portfolio",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "user",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "uint256",
        "name": "mintedAmount",
        "type": "uint256"
    }, {
        "indexed": False,
        "internalType": "uint256",
        "name": "userBalanceAfterDeposit",
        "type": "uint256"
    }],
    "name":
    "Deposited",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": False,
        "internalType": "uint8",
        "name": "version",
        "type": "uint8"
    }],
    "name":
    "Initialized",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
    }],
    "name":
    "OwnershipTransferred",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "portfolio",
        "type": "address"
    }],
    "name":
    "PublicSwapEnabled",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "from",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "to",
        "type": "address"
    }, {
        "indexed": False,
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
    }],
    "name":
    "Transfer",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "implementation",
        "type": "address"
    }],
    "name":
    "Upgraded",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": False,
        "internalType": "uint256[]",
        "name": "depositedAmounts",
        "type": "uint256[]"
    }, {
        "indexed": False,
        "internalType": "address[]",
        "name": "portfolioTokens",
        "type": "address[]"
    }],
    "name":
    "UserDepositedAmounts",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "user",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "uint256",
        "name": "burnedAmount",
        "type": "uint256"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "portfolio",
        "type": "address"
    }, {
        "indexed": False,
        "internalType": "address[]",
        "name": "portfolioTokens",
        "type": "address[]"
    }, {
        "indexed": False,
        "internalType": "uint256",
        "name": "userBalanceAfterWithdrawal",
        "type": "uint256"
    }, {
        "indexed": False,
        "internalType": "uint256[]",
        "name": "userWithdrawalAmounts",
        "type": "uint256[]"
    }],
    "name":
    "Withdrawn",
    "type":
    "event"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "name":
    "_lastDepositTime",
    "outputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "name":
    "_lastWithdrawCooldown",
    "outputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "accessController",
    "outputs": [{
        "internalType": "contract IAccessController",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "owner",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "spender",
        "type": "address"
    }],
    "name":
    "allowance",
    "outputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "spender",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
    }],
    "name":
    "approve",
    "outputs": [{
        "internalType": "bool",
        "name": "",
        "type": "bool"
    }],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "assetManagementConfig",
    "outputs": [{
        "internalType": "contract IAssetManagementConfig",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "account",
        "type": "address"
    }],
    "name":
    "balanceOf",
    "outputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_target",
        "type": "address"
    }, {
        "internalType": "bytes",
        "name": "_claimCalldata",
        "type": "bytes"
    }],
    "name":
    "claimRewardTokens",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [],
    "name": "decimals",
    "outputs": [{
        "internalType": "uint8",
        "name": "",
        "type": "uint8"
    }],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "spender",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "subtractedValue",
        "type": "uint256"
    }],
    "name":
    "decreaseAllowance",
    "outputs": [{
        "internalType": "bool",
        "name": "",
        "type": "bool"
    }],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "uint256",
        "name": "_portfolioTokenAmount",
        "type": "uint256"
    }, {
        "internalType": "address[]",
        "name": "_exemptionTokens",
        "type": "address[]"
    }],
    "name":
    "emergencyWithdrawal",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_withdrawFor",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "_tokenReceiver",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "_portfolioTokenAmount",
        "type": "uint256"
    }, {
        "internalType": "address[]",
        "name": "_exemptionTokens",
        "type": "address[]"
    }],
    "name":
    "emergencyWithdrawalFor",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "feeModule",
    "outputs": [{
        "internalType": "contract IFeeModule",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address[]",
        "name": "portfolioTokens",
        "type": "address[]"
    }, {
        "internalType": "address",
        "name": "_vault",
        "type": "address"
    }],
    "name":
    "getTokenBalancesOf",
    "outputs": [{
        "internalType": "uint256[]",
        "name": "vaultBalances",
        "type": "uint256[]"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "getTokens",
    "outputs": [{
        "internalType": "address[]",
        "name": "",
        "type": "address[]"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "contract IPriceOracle",
        "name": "_oracle",
        "type": "address"
    }, {
        "internalType": "address[]",
        "name": "_tokens",
        "type": "address[]"
    }, {
        "internalType": "uint256",
        "name": "_totalSupply",
        "type": "uint256"
    }, {
        "internalType": "address",
        "name": "_vault",
        "type": "address"
    }],
    "name":
    "getVaultValueInUSD",
    "outputs": [{
        "internalType": "uint256",
        "name": "vaultValue",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "spender",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "addedValue",
        "type": "uint256"
    }],
    "name":
    "increaseAllowance",
    "outputs": [{
        "internalType": "bool",
        "name": "",
        "type": "bool"
    }],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "components": [{
            "internalType": "string",
            "name": "_name",
            "type": "string"
        }, {
            "internalType": "string",
            "name": "_symbol",
            "type": "string"
        }, {
            "internalType": "address",
            "name": "_vault",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_module",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_tokenExclusionManager",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_accessController",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_protocolConfig",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_assetManagementConfig",
            "type": "address"
        }, {
            "internalType": "address",
            "name": "_feeModule",
            "type": "address"
        }],
        "internalType":
        "struct FunctionParameters.PortfolioInitData",
        "name":
        "initData",
        "type":
        "tuple"
    }],
    "name":
    "init",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address[]",
        "name": "_tokens",
        "type": "address[]"
    }],
    "name":
    "initToken",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_to",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
    }],
    "name":
    "mintShares",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "uint256[]",
        "name": "depositAmounts",
        "type": "uint256[]"
    }, {
        "internalType": "uint256",
        "name": "_minMintAmount",
        "type": "uint256"
    }, {
        "components": [{
            "components": [{
                "internalType": "address",
                "name": "token",
                "type": "address"
            }, {
                "internalType": "uint160",
                "name": "amount",
                "type": "uint160"
            }, {
                "internalType": "uint48",
                "name": "expiration",
                "type": "uint48"
            }, {
                "internalType": "uint48",
                "name": "nonce",
                "type": "uint48"
            }],
            "internalType":
            "struct IAllowanceTransfer.PermitDetails[]",
            "name":
            "details",
            "type":
            "tuple[]"
        }, {
            "internalType": "address",
            "name": "spender",
            "type": "address"
        }, {
            "internalType": "uint256",
            "name": "sigDeadline",
            "type": "uint256"
        }],
        "internalType":
        "struct IAllowanceTransfer.PermitBatch",
        "name":
        "_permit",
        "type":
        "tuple"
    }, {
        "internalType": "bytes",
        "name": "_signature",
        "type": "bytes"
    }],
    "name":
    "multiTokenDeposit",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_depositFor",
        "type": "address"
    }, {
        "internalType": "uint256[]",
        "name": "depositAmounts",
        "type": "uint256[]"
    }, {
        "internalType": "uint256",
        "name": "_minMintAmount",
        "type": "uint256"
    }],
    "name":
    "multiTokenDepositFor",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "uint256",
        "name": "_portfolioTokenAmount",
        "type": "uint256"
    }],
    "name":
    "multiTokenWithdrawal",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_withdrawFor",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "_tokenReceiver",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "_portfolioTokenAmount",
        "type": "uint256"
    }],
    "name":
    "multiTokenWithdrawalFor",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "name",
    "outputs": [{
        "internalType": "string",
        "name": "",
        "type": "string"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "owner",
    "outputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "permit2",
    "outputs": [{
        "internalType": "contract IAllowanceTransfer",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "protocolConfig",
    "outputs": [{
        "internalType": "contract IProtocolConfig",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "proxiableUUID",
    "outputs": [{
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_token",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
    }, {
        "internalType": "address",
        "name": "_to",
        "type": "address"
    }],
    "name":
    "pullFromVault",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "inputs": [],
    "name":
    "safeModule",
    "outputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "symbol",
    "outputs": [{
        "internalType": "string",
        "name": "",
        "type": "string"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "tokenExclusionManager",
    "outputs": [{
        "internalType": "contract ITokenExclusionManager",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "totalSupply",
    "outputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "to",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
    }],
    "name":
    "transfer",
    "outputs": [{
        "internalType": "bool",
        "name": "",
        "type": "bool"
    }],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "from",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "to",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
    }],
    "name":
    "transferFrom",
    "outputs": [{
        "internalType": "bool",
        "name": "",
        "type": "bool"
    }],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
    }],
    "name":
    "transferOwnership",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address[]",
        "name": "_tokens",
        "type": "address[]"
    }],
    "name":
    "updateTokenList",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "newImplementation",
        "type": "address"
    }],
    "name":
    "upgradeTo",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "newImplementation",
        "type": "address"
    }, {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
    }],
    "name":
    "upgradeToAndCall",
    "outputs": [],
    "stateMutability":
    "payable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "name":
    "userCooldownPeriod",
    "outputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "name":
    "userLastDepositTime",
    "outputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "vault",
    "outputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}]

permit_abi = [{
    "type":
    "function",
    "name":
    "DOMAIN_SEPARATOR",
    "inputs": [],
    "outputs": [{
        "name": "",
        "type": "bytes32",
        "internalType": "bytes32"
    }],
    "stateMutability":
    "view"
}, {
    "type":
    "function",
    "name":
    "allowance",
    "inputs": [{
        "name": "user",
        "type": "address",
        "internalType": "address"
    }, {
        "name": "token",
        "type": "address",
        "internalType": "address"
    }, {
        "name": "spender",
        "type": "address",
        "internalType": "address"
    }],
    "outputs": [{
        "name": "amount",
        "type": "uint160",
        "internalType": "uint160"
    }, {
        "name": "expiration",
        "type": "uint48",
        "internalType": "uint48"
    }, {
        "name": "nonce",
        "type": "uint48",
        "internalType": "uint48"
    }],
    "stateMutability":
    "view"
}, {
    "type":
    "function",
    "name":
    "approve",
    "inputs": [{
        "name": "token",
        "type": "address",
        "internalType": "address"
    }, {
        "name": "spender",
        "type": "address",
        "internalType": "address"
    }, {
        "name": "amount",
        "type": "uint160",
        "internalType": "uint160"
    }, {
        "name": "expiration",
        "type": "uint48",
        "internalType": "uint48"
    }],
    "outputs": [],
    "stateMutability":
    "nonpayable"
}, {
    "type":
    "function",
    "name":
    "invalidateNonces",
    "inputs": [{
        "name": "token",
        "type": "address",
        "internalType": "address"
    }, {
        "name": "spender",
        "type": "address",
        "internalType": "address"
    }, {
        "name": "newNonce",
        "type": "uint48",
        "internalType": "uint48"
    }],
    "outputs": [],
    "stateMutability":
    "nonpayable"
}, {
    "type":
    "function",
    "name":
    "lockdown",
    "inputs": [{
        "name":
        "approvals",
        "type":
        "tuple[]",
        "internalType":
        "struct IAllowanceTransfer.TokenSpenderPair[]",
        "components": [{
            "name": "token",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "spender",
            "type": "address",
            "internalType": "address"
        }]
    }],
    "outputs": [],
    "stateMutability":
    "nonpayable"
}, {
    "type":
    "function",
    "name":
    "permit",
    "inputs": [{
        "name": "owner",
        "type": "address",
        "internalType": "address"
    }, {
        "name":
        "permitBatch",
        "type":
        "tuple",
        "internalType":
        "struct IAllowanceTransfer.PermitBatch",
        "components": [{
            "name":
            "details",
            "type":
            "tuple[]",
            "internalType":
            "struct IAllowanceTransfer.PermitDetails[]",
            "components": [{
                "name": "token",
                "type": "address",
                "internalType": "address"
            }, {
                "name": "amount",
                "type": "uint160",
                "internalType": "uint160"
            }, {
                "name": "expiration",
                "type": "uint48",
                "internalType": "uint48"
            }, {
                "name": "nonce",
                "type": "uint48",
                "internalType": "uint48"
            }]
        }, {
            "name": "spender",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "sigDeadline",
            "type": "uint256",
            "internalType": "uint256"
        }]
    }, {
        "name": "signature",
        "type": "bytes",
        "internalType": "bytes"
    }],
    "outputs": [],
    "stateMutability":
    "nonpayable"
}, {
    "type":
    "function",
    "name":
    "permit",
    "inputs": [{
        "name": "owner",
        "type": "address",
        "internalType": "address"
    }, {
        "name":
        "permitSingle",
        "type":
        "tuple",
        "internalType":
        "struct IAllowanceTransfer.PermitSingle",
        "components": [{
            "name":
            "details",
            "type":
            "tuple",
            "internalType":
            "struct IAllowanceTransfer.PermitDetails",
            "components": [{
                "name": "token",
                "type": "address",
                "internalType": "address"
            }, {
                "name": "amount",
                "type": "uint160",
                "internalType": "uint160"
            }, {
                "name": "expiration",
                "type": "uint48",
                "internalType": "uint48"
            }, {
                "name": "nonce",
                "type": "uint48",
                "internalType": "uint48"
            }]
        }, {
            "name": "spender",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "sigDeadline",
            "type": "uint256",
            "internalType": "uint256"
        }]
    }, {
        "name": "signature",
        "type": "bytes",
        "internalType": "bytes"
    }],
    "outputs": [],
    "stateMutability":
    "nonpayable"
}, {
    "type":
    "function",
    "name":
    "transferFrom",
    "inputs": [{
        "name":
        "transferDetails",
        "type":
        "tuple[]",
        "internalType":
        "struct IAllowanceTransfer.AllowanceTransferDetails[]",
        "components": [{
            "name": "from",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "to",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint160",
            "internalType": "uint160"
        }, {
            "name": "token",
            "type": "address",
            "internalType": "address"
        }]
    }],
    "outputs": [],
    "stateMutability":
    "nonpayable"
}, {
    "type":
    "function",
    "name":
    "transferFrom",
    "inputs": [{
        "name": "from",
        "type": "address",
        "internalType": "address"
    }, {
        "name": "to",
        "type": "address",
        "internalType": "address"
    }, {
        "name": "amount",
        "type": "uint160",
        "internalType": "uint160"
    }, {
        "name": "token",
        "type": "address",
        "internalType": "address"
    }],
    "outputs": [],
    "stateMutability":
    "nonpayable"
}, {
    "type":
    "event",
    "name":
    "Approval",
    "inputs": [{
        "name": "owner",
        "type": "address",
        "indexed": True,
        "internalType": "address"
    }, {
        "name": "token",
        "type": "address",
        "indexed": True,
        "internalType": "address"
    }, {
        "name": "spender",
        "type": "address",
        "indexed": True,
        "internalType": "address"
    }, {
        "name": "amount",
        "type": "uint160",
        "indexed": False,
        "internalType": "uint160"
    }, {
        "name": "expiration",
        "type": "uint48",
        "indexed": False,
        "internalType": "uint48"
    }],
    "anonymous":
    False
}, {
    "type":
    "event",
    "name":
    "Lockdown",
    "inputs": [{
        "name": "owner",
        "type": "address",
        "indexed": True,
        "internalType": "address"
    }, {
        "name": "token",
        "type": "address",
        "indexed": False,
        "internalType": "address"
    }, {
        "name": "spender",
        "type": "address",
        "indexed": False,
        "internalType": "address"
    }],
    "anonymous":
    False
}, {
    "type":
    "event",
    "name":
    "NonceInvalidation",
    "inputs": [{
        "name": "owner",
        "type": "address",
        "indexed": True,
        "internalType": "address"
    }, {
        "name": "token",
        "type": "address",
        "indexed": True,
        "internalType": "address"
    }, {
        "name": "spender",
        "type": "address",
        "indexed": True,
        "internalType": "address"
    }, {
        "name": "newNonce",
        "type": "uint48",
        "indexed": False,
        "internalType": "uint48"
    }, {
        "name": "oldNonce",
        "type": "uint48",
        "indexed": False,
        "internalType": "uint48"
    }],
    "anonymous":
    False
}, {
    "type":
    "event",
    "name":
    "Permit",
    "inputs": [{
        "name": "owner",
        "type": "address",
        "indexed": True,
        "internalType": "address"
    }, {
        "name": "token",
        "type": "address",
        "indexed": True,
        "internalType": "address"
    }, {
        "name": "spender",
        "type": "address",
        "indexed": True,
        "internalType": "address"
    }, {
        "name": "amount",
        "type": "uint160",
        "indexed": False,
        "internalType": "uint160"
    }, {
        "name": "expiration",
        "type": "uint48",
        "indexed": False,
        "internalType": "uint48"
    }, {
        "name": "nonce",
        "type": "uint48",
        "indexed": False,
        "internalType": "uint48"
    }],
    "anonymous":
    False
}, {
    "type":
    "error",
    "name":
    "AllowanceExpired",
    "inputs": [{
        "name": "deadline",
        "type": "uint256",
        "internalType": "uint256"
    }]
}, {
    "type": "error",
    "name": "ExcessiveInvalidation",
    "inputs": []
}, {
    "type":
    "error",
    "name":
    "InsufficientAllowance",
    "inputs": [{
        "name": "amount",
        "type": "uint256",
        "internalType": "uint256"
    }]
}]

erc20_abi = [{
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "owner",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "spender",
        "type": "address"
    }, {
        "indexed": False,
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
    }],
    "name":
    "Approval",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "from",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "to",
        "type": "address"
    }, {
        "indexed": False,
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
    }],
    "name":
    "Transfer",
    "type":
    "event"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "owner",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "spender",
        "type": "address"
    }],
    "name":
    "allowance",
    "outputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "spender",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
    }],
    "name":
    "approve",
    "outputs": [{
        "internalType": "bool",
        "name": "",
        "type": "bool"
    }],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "account",
        "type": "address"
    }],
    "name":
    "balanceOf",
    "outputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "decimals",
    "outputs": [{
        "internalType": "uint8",
        "name": "",
        "type": "uint8"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "spender",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "subtractedValue",
        "type": "uint256"
    }],
    "name":
    "decreaseAllowance",
    "outputs": [{
        "internalType": "bool",
        "name": "",
        "type": "bool"
    }],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "spender",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "addedValue",
        "type": "uint256"
    }],
    "name":
    "increaseAllowance",
    "outputs": [{
        "internalType": "bool",
        "name": "",
        "type": "bool"
    }],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "name",
    "outputs": [{
        "internalType": "string",
        "name": "",
        "type": "string"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "symbol",
    "outputs": [{
        "internalType": "string",
        "name": "",
        "type": "string"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "totalSupply",
    "outputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "recipient",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
    }],
    "name":
    "transfer",
    "outputs": [{
        "internalType": "bool",
        "name": "",
        "type": "bool"
    }],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "sender",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "recipient",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
    }],
    "name":
    "transferFrom",
    "outputs": [{
        "internalType": "bool",
        "name": "",
        "type": "bool"
    }],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}]

rebalance_abi = [{
    "inputs": [],
    "stateMutability": "nonpayable",
    "type": "constructor"
}, {
    "inputs": [],
    "name": "BalanceOfHandlerShouldNotExceedDust",
    "type": "error"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "name":
    "BalanceOfVaultCannotNotBeZero",
    "type":
    "error"
}, {
    "inputs": [],
    "name": "BalanceOfVaultIsZero",
    "type": "error"
}, {
    "inputs": [],
    "name": "CallerNotAssetManager",
    "type": "error"
}, {
    "inputs": [],
    "name": "ClaimFailed",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidAddress",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidBuyTokenList",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidLength",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidSolver",
    "type": "error"
}, {
    "inputs": [],
    "name": "InvalidTokenRemovalPercentage",
    "type": "error"
}, {
    "inputs": [],
    "name": "IsPortfolioToken",
    "type": "error"
}, {
    "inputs": [],
    "name": "NonPortfolioTokenBalanceIsNotZero",
    "type": "error"
}, {
    "inputs": [],
    "name": "NotPortfolioToken",
    "type": "error"
}, {
    "inputs": [],
    "name": "ProtocolIsPaused",
    "type": "error"
}, {
    "inputs": [],
    "name": "RewardTargetNotEnabled",
    "type": "error"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": False,
        "internalType": "address",
        "name": "previousAdmin",
        "type": "address"
    }, {
        "indexed": False,
        "internalType": "address",
        "name": "newAdmin",
        "type": "address"
    }],
    "name":
    "AdminChanged",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "beacon",
        "type": "address"
    }],
    "name":
    "BeaconUpgraded",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": False,
        "internalType": "uint8",
        "name": "version",
        "type": "uint8"
    }],
    "name":
    "Initialized",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
    }],
    "name":
    "OwnershipTransferred",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "token",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "address",
        "name": "vault",
        "type": "address"
    }, {
        "indexed": True,
        "internalType": "uint256",
        "name": "balance",
        "type": "uint256"
    }, {
        "indexed": False,
        "internalType": "uint256",
        "name": "atSnapshotId",
        "type": "uint256"
    }],
    "name":
    "PortfolioTokenRemoved",
    "type":
    "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": False,
        "internalType": "address[]",
        "name": "newTokens",
        "type": "address[]"
    }],
    "name":
    "UpdatedTokens",
    "type":
    "event"
}, {
    "anonymous": False,
    "inputs": [],
    "name": "UpdatedWeights",
    "type": "event"
}, {
    "anonymous":
    False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "implementation",
        "type": "address"
    }],
    "name":
    "Upgraded",
    "type":
    "event"
}, {
    "inputs": [],
    "name":
    "TOTAL_WEIGHT",
    "outputs": [{
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "accessController",
    "outputs": [{
        "internalType": "contract IAccessController",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "assetManagementConfig",
    "outputs": [{
        "internalType": "contract IAssetManagementConfig",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_tokenToBeClaimed",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "_target",
        "type": "address"
    }, {
        "internalType": "bytes",
        "name": "_claimCalldata",
        "type": "bytes"
    }],
    "name":
    "claimRewardTokens",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address[]",
        "name": "portfolioTokens",
        "type": "address[]"
    }, {
        "internalType": "address",
        "name": "_vault",
        "type": "address"
    }],
    "name":
    "getTokenBalancesOf",
    "outputs": [{
        "internalType": "uint256[]",
        "name": "vaultBalances",
        "type": "uint256[]"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_portfolio",
        "type": "address"
    }, {
        "internalType": "address",
        "name": "_accessController",
        "type": "address"
    }],
    "name":
    "init",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "owner",
    "outputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "portfolio",
    "outputs": [{
        "internalType": "contract IPortfolio",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "protocolConfig",
    "outputs": [{
        "internalType": "contract IProtocolConfig",
        "name": "",
        "type": "address"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [],
    "name":
    "proxiableUUID",
    "outputs": [{
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_token",
        "type": "address"
    }],
    "name":
    "removeNonPortfolioToken",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_token",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "_percentage",
        "type": "uint256"
    }],
    "name":
    "removeNonPortfolioTokenPartially",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_token",
        "type": "address"
    }],
    "name":
    "removePortfolioToken",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "_token",
        "type": "address"
    }, {
        "internalType": "uint256",
        "name": "_percentage",
        "type": "uint256"
    }],
    "name":
    "removePortfolioTokenPartially",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "",
        "type": "address"
    }],
    "name":
    "tokensMapping",
    "outputs": [{
        "internalType": "bool",
        "name": "",
        "type": "bool"
    }],
    "stateMutability":
    "view",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
    }],
    "name":
    "transferOwnership",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "components": [{
            "internalType": "address[]",
            "name": "_newTokens",
            "type": "address[]"
        }, {
            "internalType": "address[]",
            "name": "_sellTokens",
            "type": "address[]"
        }, {
            "internalType": "uint256[]",
            "name": "_sellAmounts",
            "type": "uint256[]"
        }, {
            "internalType": "address",
            "name": "_handler",
            "type": "address"
        }, {
            "internalType": "bytes",
            "name": "_callData",
            "type": "bytes"
        }],
        "internalType":
        "struct FunctionParameters.RebalanceIntent",
        "name":
        "rebalanceData",
        "type":
        "tuple"
    }],
    "name":
    "updateTokens",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address[]",
        "name": "_sellTokens",
        "type": "address[]"
    }, {
        "internalType": "uint256[]",
        "name": "_sellAmounts",
        "type": "uint256[]"
    }, {
        "internalType": "address",
        "name": "_handler",
        "type": "address"
    }, {
        "internalType": "bytes",
        "name": "_callData",
        "type": "bytes"
    }],
    "name":
    "updateWeights",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "newImplementation",
        "type": "address"
    }],
    "name":
    "upgradeTo",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "address",
        "name": "newImplementation",
        "type": "address"
    }, {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
    }],
    "name":
    "upgradeToAndCall",
    "outputs": [],
    "stateMutability":
    "payable",
    "type":
    "function"
}]


#Function to get details of transaction on Velvet Capital
def invoke_contract_and_parse_logs():
    """
    Get the details of of a specific transaction in the agent's wallet.


    Returns:
        str: A message showing the details of the transactions hash
    """

    try:
        portfolio_info_args = []
        # Invoke the contract method
        print("Invoking contract method...")

        # Wait for the transaction to be mined
        receipt = web3.eth.get_transaction_receipt(
            "0x61dc494a66c1f9871cc3b7e57a3f692ad4cdd8a44e5714edc9d7a23f01b17cc0"
        )

        # Log transaction details
        # print("Transaction successful!", receipt)
        print(f"Transaction Hash: {receipt.transactionHash.hex()}")

        contract = web3.eth.contract(
            address="0xf93659fb357899e092813bc3a2959ceDb3282a7f",
            abi=portfolio_abi)

        logs = contract.events.PortfolioInfo().process_receipt(receipt)
        found_events = False

        # Extract all event names from the ABI
        event_names = [
            item['name'] for item in portfolio_abi if item['type'] == 'event'
        ]
        print(event_names)

        # Loop through each log in the transaction receipt
        for log in receipt['logs']:

            # Try each event in the ABI to decode the log
            for event_name in event_names:
                if event_name == "PortfolioInfo":
                    event = getattr(contract.events, event_name)
                    try:
                        print(event_name)
                        # Attempt to parse the log with the current event
                        parsed_log = event().process_log(log)

                        # If parsing succeeds, print the event details
                        print(f"Event Name: {parsed_log['event']}")
                        print("Arguments:", parsed_log['args'])
                        portfolio_info_args.append(parsed_log['args'])
                        found_events = True
                        break  # Move to the next log after a successful match
                    except Exception:
                        # Ignore logs that don't match the current event
                        pass

        # If no PortfolioInfo events were found, print a message

            print(portfolio_info_args, "portfolio_info_args")
            return portfolio_info_args
    except Exception as e:
        print("An error occurred while invoking the contract:")
        print(e)


#Function to create a portfolio on Velvet Capital


def create_portfolio_non_custodial(array_tokens):
    """
    Invokes the createPortfolioNonCustodial function on the Portfolio     Factory contract with hardcoded parameters.

    Args:
    tokens (str): The "," seprated  token addressess
    """

    # Define the ABI for the createPortfolioNonCustodial function

    abi = [{
        "inputs": [{
            "internalType":
            "struct FunctionParameters.PortfolioCreationInitData",
            "name":
            "initData",
            "type":
            "tuple",
            "components": [{
                "internalType": "address",
                "name": "_assetManagerTreasury",
                "type": "address"
            }, {
                "internalType": "address[]",
                "name": "_whitelistedTokens",
                "type": "address[]"
            }, {
                "internalType": "uint256",
                "name": "_managementFee",
                "type": "uint256"
            }, {
                "internalType": "uint256",
                "name": "_performanceFee",
                "type": "uint256"
            }, {
                "internalType": "uint256",
                "name": "_entryFee",
                "type": "uint256"
            }, {
                "internalType": "uint256",
                "name": "_exitFee",
                "type": "uint256"
            }, {
                "internalType": "uint256",
                "name": "_initialPortfolioAmount",
                "type": "uint256"
            }, {
                "internalType": "uint256",
                "name": "_minPortfolioTokenHoldingAmount",
                "type": "uint256"
            }, {
                "internalType": "bool",
                "name": "_public",
                "type": "bool"
            }, {
                "internalType": "bool",
                "name": "_transferable",
                "type": "bool"
            }, {
                "internalType": "bool",
                "name": "_transferableToPublic",
                "type": "bool"
            }, {
                "internalType": "bool",
                "name": "_whitelistTokens",
                "type": "bool"
            }, {
                "internalType": "string",
                "name": "_name",
                "type": "string"
            }, {
                "internalType": "string",
                "name": "_symbol",
                "type": "string"
            }]
        }],
        "name":
        "createPortfolioNonCustodial",
        "outputs": [],
        "stateMutability":
        "nonpayable",
        "type":
        "function"
    }]
    # Hardcoded parameters
    asset_manager_treasury = "0x000000000000000000000000000000000000dead"
    whitelisted_tokens = []
    management_fee = "100"
    performance_fee = "100"
    entry_fee = "100"
    exit_fee = "100"
    initial_portfolio_amount = "1000000000000000000"
    min_portfolio_token_holding_amount = "1000000000000000000"
    is_public = True
    is_transferable = True
    transferable_to_public = True
    whitelist_tokens = False
    name = "AItest"
    symbol = "AIT"

    portfolio_info_args = []
    # Prepare the arguments for the function call as a list
    init_data = [
        asset_manager_treasury, whitelisted_tokens, management_fee,
        performance_fee, entry_fee, exit_fee, initial_portfolio_amount,
        min_portfolio_token_holding_amount, is_public, is_transferable,
        transferable_to_public, whitelist_tokens, name, symbol
    ]

    found_events = False

    # Extract all event names from the ABI

    # Invoke the contract function using the Coinbase Wallet SDK?
    receipt = None
    try:
        invocation = agent_wallet.invoke_contract(
            contract_address="0xf93659fb357899e092813bc3a2959ceDb3282a7f",
            abi=abi,
            method="createPortfolioNonCustodial",
            args={"initData": init_data})
        # Wait for the transaction to be mined
        tx = invocation.wait()
        print(tx.transaction_hash)

        contract = web3.eth.contract(
            address="0xf93659fb357899e092813bc3a2959ceDb3282a7f",
            abi=portfolio_abi)

        receipt = web3.eth.get_transaction_receipt(tx.transaction_hash)
        event_names = [
            item['name'] for item in portfolio_abi if item['type'] == 'event'
        ]
        # print(event_names)
        for log in receipt['logs']:

            # Try each event in the ABI to decode the log
            for event_name in event_names:
                if event_name == "PortfolioInfo":
                    event = getattr(contract.events, event_name)
                    try:
                        # print(event_name)
                        # Attempt to parse the log with the current event
                        parsed_log = event().process_log(log)

                        # If parsing succeeds, print the event details
                        # print(f"Event Name: {parsed_log['event']}")
                        # print("Arguments:", parsed_log['args'])
                        portfolio_info_args.append(parsed_log['args'])
                        found_events = True
                        break  # Move to the next log after a successful match
                    except Exception:
                        # Ignore logs that don't match the current event
                        pass

        # If no PortfolioInfo events were found, print a message
        if not found_events:
            print("No PortfolioInfo events found in this transaction.")

        # print(portfolio_info_args[0], "portfolio_info_args")
        print(portfolio_info_args[0].portfolioData.portfolio, "portfolio")
        print(portfolio_info_args[0].portfolioData.rebalancing, "rebalancing")
        print(portfolio_info_args[0].portfolioData.vaultAddress,
              "vaultAddress")

        print("===================================")
        initabi = [{
            "inputs": [{
                "internalType": "address[]",
                "name": "_tokens",
                "type": "address[]"
            }],
            "name":
            "initToken",
            "outputs": [],
            "stateMutability":
            "nonpayable",
            "type":
            "function"
        }]
        tokens_list = array_tokens.split(",")
        print(tokens_list)
        print("==================")
        initFund = agent_wallet.invoke_contract(
            contract_address=portfolio_info_args[0].portfolioData.portfolio,
            abi=fund_abi,
            method="initToken",
            args={"_tokens": tokens_list})
        # Wait for the transaction to be mined
        transaction_init = initFund.wait()
        print("init", transaction_init.transaction_hash)
        return receipt

    except Exception as e:
        print(f"An error occurred: {e}")
        # print(f"Transaction Hash: {receipt}")
        return receipt


# initalize a portfolio with tokens
def initalize_portfolio(portfolio_address, token_array):
    """
        Initalize a portfolio.

        Args:
            Portfolio - address (str): The address of the portfolio
            tokens (str[]): The array of the token addressess

        Returns:
            str: A Initalize details
        """
    return null


# Function to Deposit in portfolio


def deposit_portfolio_permit(user_address, portfolioAddress):
    try:

        buy_address = Web3.to_checksum_address(
            user_address)  # Replace with actual address if necessary
        print(buy_address)
        gas_price = web3.eth.gas_price
        # print(gas_price)
        # Contract Instances
        address = portfolioAddress
        checksum_address = Web3.to_checksum_address(address)
        print(checksum_address)
        contract_instance = web3.eth.contract(address=checksum_address,
                                              abi=fund_abi)

        # Fetch tokens from the contract

        tokens = contract_instance.functions.getTokens().call(
            {'from': checksum_address})
        print(tokens)
        if not tokens or not isinstance(tokens, list) or len(tokens) == 0:

            raise ValueError("Failed to fetch tokens or no tokens available")
        amount = []
        # Approval checks and approvals
        for elem in tokens:
            erc20_instance = web3.eth.contract(
                address=Web3.to_checksum_address(elem), abi=erc20_abi)
            print(elem, "elem")
            balance = erc20_instance.functions.balanceOf(buy_address).call()
            print(balance, "balance")
            amount.append(str(balance))
            # if float(allowance) < float(elem['amount']):
            approval_token = agent_wallet.invoke_contract(
                contract_address=Web3.to_checksum_address(elem),
                abi=erc20_abi,
                method="approve",
                args={
                    "spender": checksum_address,
                    "amount": "100000000000000000000000"
                }).wait()

        print(
            "allowance",
            amount,
        )

        deposit_token = agent_wallet.invoke_contract(
            contract_address=checksum_address,
            abi=fund_abi,
            method="multiTokenDepositFor",
            args={
                "_depositFor": buy_address,
                "depositAmounts":
                amount,  # replace with actual deposit amounts as needed
                "_minMintAmount":
                "0"  # replace with the minimum mint amount you want
            }).wait()
        print(deposit_token)

        deposit_token.wait()

    except Exception as error:
        print(f"An error occurred: {error}")


def withdraw_portfolio(user_address, portfolioAddress):
    try:

        buy_address = Web3.to_checksum_address(
            user_address)  # Replace with actual address if necessary
        print(buy_address)
        gas_price = web3.eth.gas_price
        # print(gas_price)
        # Contract Instances
        address = portfolioAddress
        checksum_address = Web3.to_checksum_address(address)
        print(checksum_address)
        contract_instance = web3.eth.contract(address=checksum_address,
                                              abi=fund_abi)

        # Fetch tokens from the contract

        balance = contract_instance.functions.balanceOf(buy_address).call()
        print(balance)

        withdraw_token = agent_wallet.invoke_contract(
            contract_address=checksum_address,
            abi=fund_abi,
            method="multiTokenWithdrawal",
            args={
                "_portfolioTokenAmount": str(
                    balance
                )  # Replace 'amount' with the actual token amount you want to withdraw
            }).wait()
        print(withdraw_token)

        withdraw_token.wait()

    except Exception as error:
        print(f"An error occurred: {error}")


def rebalance_portfolio(user_address, portfolioAddress, rebalanceAddress,
                        sellToken, buyToken, remaining_tokens):
    try:
        buy_address = Web3.to_checksum_address(
            user_address)  # Replace with actual address if necessary
        print(buy_address)
        gas_price = web3.eth.gas_price
        # print(gas_price)
        # Contract Instances
        erc20_instance = web3.eth.contract(
            address=Web3.to_checksum_address(sellToken), abi=erc20_abi)
        address = portfolioAddress
        checksum_address = Web3.to_checksum_address(address)
        print(checksum_address)
        contract_instance = web3.eth.contract(address=checksum_address,
                                              abi=fund_abi)

        # Fetch tokens from the contract

        vaultData = contract_instance.functions.vault().call()
        print(vaultData)
        balance = erc20_instance.functions.balanceOf(vaultData).call()
        print(balance)
        print({
            "rebalanceAddress": rebalanceAddress,
            "sellToken": sellToken,
            "buyToken": buyToken,
            "sellAmount":
            str(balance
                ),  # Make sure this value matches the token decimal format
            "slippage": "100",
            "remainingTokens":
            remaining_tokens.split(","),  # Add remaining tokens if any
            "owner": buy_address
        })
        # Define the endpoint
        url = "https://eventsapi.velvetdao.xyz/api/v3/rebalance"

        # Define the payload for the request
        payload = {
            "rebalanceAddress": rebalanceAddress,
            "sellToken": sellToken,
            "buyToken": buyToken,
            "sellAmount":
            str(balance
                ),  # Make sure this value matches the token decimal format
            "slippage": "100",
            "remainingTokens":
            remaining_tokens.split(","),  # Add remaining tokens if any
            "owner": buy_address
        }

        # Set headers if needed, e.g., if authentication is required
        headers = {"Content-Type": "application/json"}

        # Make the POST request
        response = requests.post(url, json=payload, headers=headers)

        result = response.json()
        # print(result)
        rebalance_instance = web3.eth.contract(
            address=Web3.to_checksum_address(rebalanceAddress),
            abi=rebalance_abi)

        new_tokens = result['newTokens']
        sell_tokens = result['sellTokens']
        sell_amounts = result['sellAmounts']
        handler = result['handler']
        call_data = result['callData']
        print("===================================")
        # print({
        #     "rebalanceData": [
        #         new_tokens,  # List of new token addresses
        #         sell_tokens,  # List of tokens to sell
        #         sell_amounts,  # List of amounts to sell (in token decimals)
        #         Web3.to_checksum_address(handler),  # Handler contract address
        #         call_data  # Encoded call data in bytes
        #     ]
        # })
        print("===================================")
        print(agent_wallet)
        rebalance_token = agent_wallet.invoke_contract(
            contract_address=Web3.to_checksum_address(rebalanceAddress),
            abi=rebalance_abi,
            method="updateTokens",
            args={
                "rebalanceData": [
                    [Web3.to_checksum_address(buyToken)
                     ],  # List of new token addresses
                    [Web3.to_checksum_address(sellToken)
                     ],  # List of tokens to sell
                    sell_amounts,  # List of amounts to sell (in token decimals)
                    Web3.to_checksum_address(
                        handler),  # Handler contract address
                    call_data  # Encoded call data in bytes
                ]
            }).wait()
        print(rebalance_token)

        rebalance_token.wait()

    except Exception as error:
        print(f"An error occurred: {error}")


# Helper function definitions assumed to be available:
# - AllowanceTransfer.get_permit_data


# Function to create a new ERC-20 token
def create_token(name, symbol, initial_supply):
    """
    Create a new ERC-20 token.
    
    Args:
        name (str): The name of the token
        symbol (str): The symbol of the token
        initial_supply (int): The initial supply of tokens
    
    Returns:
        str: A message confirming the token creation with details
    """
    deployed_contract = agent_wallet.deploy_token(name, symbol, initial_supply)
    deployed_contract.wait()
    return f"Token {name} ({symbol}) created with initial supply of {initial_supply} and contract address {deployed_contract.contract_address}"


# Function to transfer assets
def transfer_asset(amount, asset_id, destination_address):
    """
    Transfer an asset to a specific address.
    
    Args:
        amount (Union[int, float, Decimal]): Amount to transfer
        asset_id (str): Asset identifier ("eth", "usdc") or contract address of an ERC-20 token
        destination_address (str): Recipient's address
    
    Returns:
        str: A message confirming the transfer or describing an error
    """
    try:
        # Check if we're on Base Mainnet and the asset is USDC for gasless transfer
        is_mainnet = agent_wallet.network_id == "base-mainnet"
        is_usdc = asset_id.lower() == "usdc"
        gasless = is_mainnet and is_usdc

        # For ETH and USDC, we can transfer directly without checking balance
        if asset_id.lower() in ["eth", "usdc"]:
            transfer = agent_wallet.transfer(amount,
                                             asset_id,
                                             destination_address,
                                             gasless=gasless)
            transfer.wait()
            gasless_msg = " (gasless)" if gasless else ""
            return f"Transferred {amount} {asset_id}{gasless_msg} to {destination_address}"

        # For other assets, check balance first
        try:
            balance = agent_wallet.balance(asset_id)
        except UnsupportedAssetError:
            return f"Error: The asset {asset_id} is not supported on this network. It may have been recently deployed. Please try again in about 30 minutes."

        if balance < amount:
            return f"Insufficient balance. You have {balance} {asset_id}, but tried to transfer {amount}."

        transfer = agent_wallet.transfer(amount, asset_id, destination_address)
        transfer.wait()
        return f"Transferred {amount} {asset_id} to {destination_address}"
    except Exception as e:
        return f"Error transferring asset: {str(e)}. If this is a custom token, it may have been recently deployed. Please try again in about 30 minutes, as it needs to be indexed by CDP first."


# Function to get the balance of a specific asset
def get_balance(asset_id):
    """
    Get the balance of a specific asset in the agent's wallet.
    
    Args:
        asset_id (str): Asset identifier ("eth", "usdc") or contract address of an ERC-20 token
    
    Returns:
        str: A message showing the current balance of the specified asset
    """
    balance = agent_wallet.balance(asset_id)
    return f"Current balance of {asset_id}: {balance}"

    # Function to request ETH from the faucet (testnet only)
    #def request_eth_from_faucet():
    """
    Request ETH from the Base Sepolia testnet faucet.
    
    Returns:
        str: Status message about the faucet request
    """

    #   if agent_wallet.network_id == "base-mainnet":
    #      return "Error: The faucet is only available on Base Sepolia testnet."

    # faucet_tx = agent_wallet.faucet()
    # return f"Requested ETH from faucet. Transaction: {faucet_tx}"

    # Function to generate art using DALL-E (requires separate OpenAI API key)
    # def generate_art(prompt):
    """
    Generate art using DALL-E based on a text prompt.
    
    Args:
        prompt (str): Text description of the desired artwork
    
    Returns:
        str: Status message about the art generation, including the image URL if successful
    """
    try:
        client = OpenAI()
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        return f"Generated artwork available at: {image_url}"

    except Exception as e:
        return f"Error generating artwork: {str(e)}"


# Function to deploy an ERC-721 NFT contract
def deploy_nft(name, symbol, base_uri):
    """
    Deploy an ERC-721 NFT contract.
    
    Args:
        name (str): Name of the NFT collection
        symbol (str): Symbol of the NFT collection
        base_uri (str): Base URI for token metadata
    
    Returns:
        str: Status message about the NFT deployment, including the contract address
    """
    try:
        deployed_nft = agent_wallet.deploy_nft(name, symbol, base_uri)
        deployed_nft.wait()
        contract_address = deployed_nft.contract_address

        return f"Successfully deployed NFT contract '{name}' ({symbol}) at address {contract_address} with base URI: {base_uri}"

    except Exception as e:
        return f"Error deploying NFT contract: {str(e)}"


# Function to mint an NFT
def mint_nft(contract_address, mint_to):
    """
    Mint an NFT to a specified address.
    
    Args:
        contract_address (str): Address of the NFT contract
        mint_to (str): Address to mint NFT to
    
    Returns:
        str: Status message about the NFT minting
    """
    try:
        mint_args = {"to": mint_to, "quantity": "1"}

        mint_invocation = agent_wallet.invoke_contract(
            contract_address=contract_address, method="mint", args=mint_args)
        mint_invocation.wait()

        return f"Successfully minted NFT to {mint_to}"

    except Exception as e:
        return f"Error minting NFT: {str(e)}"


# Function to swap assets (only works on Base Mainnet)
def swap_assets(amount: Union[int, float, Decimal], from_asset_id: str,
                to_asset_id: str):
    """
    Swap one asset for another using the trade function.
    This function only works on Base Mainnet.

    Args:
        amount (Union[int, float, Decimal]): Amount of the source asset to swap
        from_asset_id (str): Source asset identifier
        to_asset_id (str): Destination asset identifier

    Returns:
        str: Status message about the swap
    """
    if agent_wallet.network_id != "base-mainnet":
        return "Error: Asset swaps are only available on Base Mainnet. Current network is not Base Mainnet."

    try:
        trade = agent_wallet.trade(amount, from_asset_id, to_asset_id)
        trade.wait()
        return f"Successfully swapped {amount} {from_asset_id} for {to_asset_id}"
    except Exception as e:
        return f"Error swapping assets: {str(e)}"


# Contract addresses for Basenames
BASENAMES_REGISTRAR_CONTROLLER_ADDRESS_MAINNET = "0x4cCb0BB02FCABA27e82a56646E81d8c5bC4119a5"
BASENAMES_REGISTRAR_CONTROLLER_ADDRESS_TESTNET = "0x49aE3cC2e3AA768B1e5654f5D3C6002144A59581"
L2_RESOLVER_ADDRESS_MAINNET = "0xC6d566A56A1aFf6508b41f6c90ff131615583BCD"
L2_RESOLVER_ADDRESS_TESTNET = "0x6533C94869D28fAA8dF77cc63f9e2b2D6Cf77eBA"


# Function to create registration arguments for Basenames
def create_register_contract_method_args(base_name: str, address_id: str,
                                         is_mainnet: bool) -> dict:
    """
    Create registration arguments for Basenames.
    
    Args:
        base_name (str): The Basename (e.g., "example.base.eth" or "example.basetest.eth")
        address_id (str): The Ethereum address
        is_mainnet (bool): True if on mainnet, False if on testnet
    
    Returns:
        dict: Formatted arguments for the register contract method
    """
    w3 = Web3()

    resolver_contract = w3.eth.contract(abi=l2_resolver_abi)

    name_hash = w3.ens.namehash(base_name)

    address_data = resolver_contract.encode_abi("setAddr",
                                                args=[name_hash, address_id])

    name_data = resolver_contract.encode_abi("setName",
                                             args=[name_hash, base_name])

    register_args = {
        "request": [
            base_name.replace(".base.eth" if is_mainnet else ".basetest.eth",
                              ""),
            address_id,
            "31557600",  # 1 year in seconds
            L2_RESOLVER_ADDRESS_MAINNET
            if is_mainnet else L2_RESOLVER_ADDRESS_TESTNET,
            [address_data, name_data],
            True
        ]
    }

    return register_args


# Function to register a basename
def register_basename(basename: str, amount: float = 0.002):
    """
    Register a basename for the agent's wallet.
    
    Args:
        basename (str): The basename to register (e.g. "myname.base.eth" or "myname.basetest.eth")
        amount (float): Amount of ETH to pay for registration (default 0.002)
    
    Returns:
        str: Status message about the basename registration
    """
    address_id = agent_wallet.default_address.address_id
    is_mainnet = agent_wallet.network_id == "base-mainnet"

    suffix = ".base.eth" if is_mainnet else ".basetest.eth"
    if not basename.endswith(suffix):
        basename += suffix

    register_args = create_register_contract_method_args(
        basename, address_id, is_mainnet)

    try:
        contract_address = (BASENAMES_REGISTRAR_CONTROLLER_ADDRESS_MAINNET
                            if is_mainnet else
                            BASENAMES_REGISTRAR_CONTROLLER_ADDRESS_TESTNET)

        invocation = agent_wallet.invoke_contract(
            contract_address=contract_address,
            method="register",
            args=register_args,
            abi=registrar_abi,
            amount=amount,
            asset_id="eth",
        )
        invocation.wait()
        return f"Successfully registered basename {basename} for address {address_id}"
    except ContractLogicError as e:
        return f"Error registering basename: {str(e)}"
    except Exception as e:
        return f"Unexpected error registering basename: {str(e)}"


# Create the Based Agent with all available functions
based_agent = Agent(
    name="Based Agent",
    instructions=
    "You are a helpful agent that can interact onchain on the Base Layer 2 using the Coinbase Developer Platform SDK. You can create tokens, transfer assets, generate art, deploy NFTs, mint NFTs, register basenames, and swap assets (on mainnet only). If you ever need to know your address, it is {agent_wallet.default_address.address_id}. If you ever need funds, you can request them from the faucet. You can also deploy your own ERC-20 tokens, NFTs, and interact with them. If someone asks you to do something you can't do, you can say so, and encourage them to implement it themselves using the CDP SDK, recommend they go to docs.cdp.coinbase.com for more informaton. You can also offer to help them implement it by writing the function and telling them to add it to the agents.py file and within your list of callable functions.",
    functions=[
        create_token,
        transfer_asset,
        get_balance,
        #request_eth_from_faucet,
        #generate_art,  # Uncomment this line if you have configured the OpenAI API
        deploy_nft,
        mint_nft,
        swap_assets,
        register_basename,
        create_portfolio_non_custodial,
        invoke_contract_and_parse_logs,
        initalize_portfolio,
        deposit_portfolio_permit,
        withdraw_portfolio,
        rebalance_portfolio,
        #  post_to_twitter
    ],
)

# add the following import to the top of the file, add the code below it, and add the new functions to the based_agent.functions list
#from twitter_utils import TwitterBot

# Initialize TwitterBot with your credentials
# twitter_bot = TwitterBot(
#     api_key=os.environ.get("TWITTER_C_API"),
#     api_secret=os.environ.get("TWITTER_C_SECRET"),
#    access_token=os.environ.get("TWITTER_API_KEY"),
#     access_token_secret=os.environ.get("TWITTER_API_SECRET")
# )

# # Add these new functions to your existing functions list

# def post_to_twitter(content: str):
#     """
#    Post a message to Twitter.
#
#    Args:
#        content (str): The content to tweet
#
#    Returns:
#        str: Status message about the tweet
#    """
#   return twitter_bot.post_tweet(content)

# def check_twitter_mentions():
#     """
#     Check recent Twitter mentions.
#
#     Returns:
#         str: Formatted string of recent mentions
#     """
#     mentions = twitter_bot.read_mentions()
#     if not mentions:
#         return "No recent mentions found"

#     result = "Recent mentions:\n"
#     for mention in mentions:
#         if 'error' in mention:
#             return f"Error checking mentions: {mention['error']}"
#         result += f"- @{mention['user']}: {mention['text']}\n"
#     return result

# def reply_to_twitter_mention(tweet_id: str, content: str):
#     """
#     Reply to a specific tweet.
#
#     Args:
#         tweet_id (str): ID of the tweet to reply to
#         content (str): Content of the reply
#
#     Returns:
#         str: Status message about the reply
#     """
#     return twitter_bot.reply_to_tweet(tweet_id, content)

# def search_twitter(query: str):
#     """
#     Search for tweets matching a query.
#
#     Args:
#         query (str): Search query
#
#     Returns:
#         str: Formatted string of matching tweets
#     """
#     tweets = twitter_bot.search_tweets(query)
#     if not tweets:
#         return f"No tweets found matching query: {query}"

#     result = f"Tweets matching '{query}':\n"
#     for tweet in tweets:
#         if 'error' in tweet:
#             return f"Error searching tweets: {tweet['error']}"
#         result += f"- @{tweet['user']}: {tweet['text']}\n"
#     return result

# ABIs for smart contracts (used in basename registration)
l2_resolver_abi = [{
    "inputs": [{
        "internalType": "bytes32",
        "name": "node",
        "type": "bytes32"
    }, {
        "internalType": "address",
        "name": "a",
        "type": "address"
    }],
    "name":
    "setAddr",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "bytes32",
        "name": "node",
        "type": "bytes32"
    }, {
        "internalType": "string",
        "name": "newName",
        "type": "string"
    }],
    "name":
    "setName",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}]

registrar_abi = [{
    "inputs": [{
        "components": [{
            "internalType": "string",
            "name": "name",
            "type": "string"
        }, {
            "internalType": "address",
            "name": "owner",
            "type": "address"
        }, {
            "internalType": "uint256",
            "name": "duration",
            "type": "uint256"
        }, {
            "internalType": "address",
            "name": "resolver",
            "type": "address"
        }, {
            "internalType": "bytes[]",
            "name": "data",
            "type": "bytes[]"
        }, {
            "internalType": "bool",
            "name": "reverseRecord",
            "type": "bool"
        }],
        "internalType":
        "struct RegistrarController.RegisterRequest",
        "name":
        "request",
        "type":
        "tuple"
    }],
    "name":
    "register",
    "outputs": [],
    "stateMutability":
    "payable",
    "type":
    "function"
}]

# ABI for vault creation

vault_create_abi = [{
    "inputs": [{
        "internalType":
        "struct FunctionParameters.PortfolioCreationInitData",
        "name":
        "initData",
        "type":
        "tuple",
        "components": [{
            "internalType": "address",
            "name": "_assetManagerTreasury",
            "type": "address"
        }, {
            "internalType": "address[]",
            "name": "_whitelistedTokens",
            "type": "address[]"
        }, {
            "internalType": "uint256",
            "name": "_managementFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_performanceFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_entryFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_exitFee",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_initialPortfolioAmount",
            "type": "uint256"
        }, {
            "internalType": "uint256",
            "name": "_minPortfolioTokenHoldingAmount",
            "type": "uint256"
        }, {
            "internalType": "bool",
            "name": "_public",
            "type": "bool"
        }, {
            "internalType": "bool",
            "name": "_transferable",
            "type": "bool"
        }, {
            "internalType": "bool",
            "name": "_transferableToPublic",
            "type": "bool"
        }, {
            "internalType": "bool",
            "name": "_whitelistTokens",
            "type": "bool"
        }, {
            "internalType": "bool",
            "name": "_externalPositionManagementWhitelisted",
            "type": "bool"
        }, {
            "internalType": "string",
            "name": "_name",
            "type": "string"
        }, {
            "internalType": "string",
            "name": "_symbol",
            "type": "string"
        }]
    }],
    "name":
    "createPortfolioNonCustodial",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}]

# To add a new function:
# 1. Define your function above (follow the existing pattern)
# 2. Add appropriate error handling
# 3. Add the function to the based_agent's functions list
# 4. If your function requires new imports or global variables, add them at the top of the file
# 5. Test your new function thoroughly before deploying

# Example of adding a new function:
# def my_new_function(param1, param2):
#     """
#     Description of what this function does.
#
#     Args:
#         param1 (type): Description of param1
#         param2 (type): Description of param2
#
#     Returns:
#         type: Description of what is returned
#     """
#     try:
#         # Your function logic here
#         result = do_something(param1, param2)
#         return f"Operation successful: {result}"
#     except Exception as e:
#         return f"Error in my_new_function: {str(e)}"

# Then add to based_agent.functions:
# based_agent = Agent(
#     ...
#     functions=[
#         ...
#         my_new_function,
#     ],
# )
