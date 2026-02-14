from bot.types import ChainName


class UnsupportedChainError(ValueError):
    
    def __init__(self, chain: ChainName):
        self.args = ("Got unsupported chain", chain)