import datetime as dt
from decimal import Decimal
import binance
from curl_cffi.requests import AsyncSession
from typing import Callable
from logger import logger
from models import CryptoTransaction
from bot.types import WalletAddressLike, ChainName
from yarl import URL
from aiocache import cached
from aiocache.serializers import PickleSerializer
from ..exceptions import UnsupportedChainError
from config import TOKEN_CONTRACTS
import certifi
from aiohttp import TCPConnector


TransactionFilter = Callable[[CryptoTransaction], bool]


class CryptoCore:
    
    def __init__(self, 
                 binance_api_key: str, 
                 binance_api_secret: str,
                 oklink_api_key: str,
    ):
        self.binance_client = binance.AsyncClient(
            api_key=binance_api_key,
            api_secret=binance_api_secret,
            session_params={'connector': TCPConnector(verify_ssl=False)}
        )
        self.oklink_endpoint = 'www.oklink.com'
        self.oklink_api_key = oklink_api_key


    @cached(ttl=17, serializer=PickleSerializer())
    async def _get_binance_pay_transactions_history(self) -> list[CryptoTransaction]:
        pay_trade_history = await self.binance_client.get_pay_trade_history()
        transactions_history = []
        if not pay_trade_history['success']:
            raise ValueError(
                "binance.AsyncClient.get_pay_trade_history() did not run successfully."
                "Got mesasge: " + pay_trade_history['message']
            )
        for trade in pay_trade_history['data']:
            amount = abs(Decimal(trade['amount']))
            transaction = CryptoTransaction(
                status='Success',
                received_at=dt.datetime.fromtimestamp(trade['transactionTime'] / 1000),
                token=trade['currency'],
                chain='BP',
                to_wallet=trade['receiverInfo']['binanceId'] if 'binanceId' in trade['receiverInfo'].keys() else trade['receiverInfo']['accountId'],
                amount=amount,
                from_wallet=trade['payerInfo']['binanceId'] if 'binanceId' in trade['payerInfo'].keys() else trade['payerInfo']['accountId'] ,
                transaction_id=trade['transactionId'],
                note=trade['note'],
                additional_info=str(trade['payerInfo'])
            )
            transactions_history.append(transaction)
        return transactions_history

    @cached(ttl=17, serializer=PickleSerializer())
    async def _get_oklink_transactions_history(
        self, 
        wallet: WalletAddressLike,
        chain: ChainName,
        limit: int = 50
    ) -> list[CryptoTransaction]:
        query = {
            'chainShortName': chain,
            'address': wallet,
            'protocolType': 'token_20',
            'limit': limit,
        }
        url = URL.build(scheme='https', host=self.oklink_endpoint, query=query,
            path='/api/v5/explorer/address/token-transaction-list'
        )
        headers = {
            'OK-ACCESS-KEY': self.oklink_api_key,
        }
        async with AsyncSession() as session:
            response_json = (await session.get(str(url), headers=headers)).json()
        if response_json['code'] != '0':
            raise ValueError(
                f"OKLINK API -> {url.path} did not run successfully."
                f"Response code: {response_json['code']}\nGot mesasge: {response_json['msg']}"
            )
        transactions_history = []
        for tx in response_json['data'][0]['transactionList']:
            tx: dict
            
            token = None
            for token_ in TOKEN_CONTRACTS:
                if TOKEN_CONTRACTS[token_].get(chain):
                    for address in TOKEN_CONTRACTS[token_][chain].split('|'):
                        if address_equals(
                            tx['tokenContractAddress'], 
                            address,
                            chain=chain
                        ):
                            token = token_
                            break

                        
            if tx['amount'] == '0' or token is None: 
                continue

            transaction = CryptoTransaction(
                status='Success',
                received_at=dt.datetime.fromtimestamp(int(tx['transactionTime']) / 1000),
                token=token,
                chain=chain,
                to_wallet=tx['to'],
                amount=tx['amount'],
                from_wallet=tx['from'],
                transaction_id=tx['txId']
            )
            transactions_history.append(transaction)
        return transactions_history


    async def get_transactions_history(
        self, 
        chain: ChainName, 
        wallet: WalletAddressLike = None,
        tx_filter: TransactionFilter = None
    ) -> list[CryptoTransaction]:
        if chain == "BP":
            transactions = await self._get_binance_pay_transactions_history()
        elif chain in ("ARBITRUM", "BSC", "TRON", "POLYGON", "OPTIMISM"):
            if wallet is None:
                raise ValueError(
                    f"wallet must be specified, if you are using chain get_transactions_history in {chain} chatin"
                )
            transactions = await self._get_oklink_transactions_history(
                wallet=wallet,
                chain=chain
            )
        else:
            raise UnsupportedChainError(chain)
        if tx_filter:
            return [tx for tx in transactions if tx_filter(tx)]
        return transactions
    

def transaction_filter(transaction: CryptoTransaction, **filters):
    for attr, targer_value in filters.items():
        attr_type = CryptoTransaction.__annotations__.get(attr)
        value = getattr(transaction, attr)
        if attr_type is WalletAddressLike:
            if not address_equals(value, targer_value, chain=transaction.chain):
                return False
        else:
            if value != targer_value:
                return False
    return True

    
def address_equals(wallet1: WalletAddressLike, wallet2: WalletAddressLike, chain: ChainName):
    if chain == 'BP':
        return int(wallet1) == int(wallet2)
    elif chain in ("ARBITRUM", "BSC", "OPTIMISM", "POLYGON"):
        return str(wallet1).lower() == str(wallet2).lower()
    elif chain == 'TRON':
        return str(wallet1) == str(wallet2)
    else:
        raise UnsupportedChainError(chain)