from eth_utils import (
    decode_hex,
)

from evm.rpc.format import (
    block_to_dict,
)
from evm.rpc.modules import (
    RPCModule,
)


class Eth(RPCModule):
    '''
    All the methods defined by JSON-RPC API, starting with "eth_"...

    Any attribute without an underscore is publicly accessible.
    '''

    def accounts(self):
        raise NotImplementedError()

    def blockNumber(self):
        num = self._chain.get_canonical_head().block_number
        return hex(num)

    def coinbase(self):
        raise NotImplementedError()

    def gasPrice(self):
        raise NotImplementedError()

    def getBalance(self, address_hex, at_block):
        address = decode_hex(address_hex)
        chain = self._chain

        if at_block == 'pending':
            at_header = chain.header
        elif at_block == 'latest':
            at_header = chain.get_canonical_head()
        elif at_block == 'earliest':
            # TODO find if genesis block can be non-zero. Why does 'earliest' option even exist?
            at_header = chain.get_canonical_block_by_number(0).header
        else:
            at_header = chain.get_canonical_block_by_number(int(at_block)).header

        vm = chain.get_vm(at_header)
        with vm.state_db(read_only=True) as state:
            balance = state.get_balance(address)

        return hex(balance)

    def getBlockByHash(self, block_hash_hex, include_transactions):
        block_hash = decode_hex(block_hash_hex)
        block = self._chain.get_block_by_hash(block_hash)
        assert block.hash == block_hash

        block_dict = block_to_dict(block, self._chain, include_transactions)

        return block_dict

    def getBlockByNumber(self, block_number_hex, include_transactions):
        block_number = int(block_number_hex, 16)
        block = self._chain.get_canonical_block_by_number(block_number)
        assert block.number == block_number
        return block_to_dict(block, self._chain, include_transactions)

    def hashrate(self):
        raise NotImplementedError()

    def mining(self):
        return False

    def protocolVersion(self):
        return "54"

    def syncing(self):
        raise NotImplementedError()