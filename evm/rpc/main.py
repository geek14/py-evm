import json

from evm.rpc.modules import Eth


def generate_response(request):
    return {
        'id': request['id'],
        'jsonrpc': request['jsonrpc'],
    }


class RPCServer:
    '''
    This "server" accepts json strings requests and returns the appropriate json string response,
    meeting the protocol for JSON-RPC defined here: https://github.com/ethereum/wiki/wiki/JSON-RPC

    The key entry point for all requests is :meth:`RPCServer.request`, which
    then proxies to the appropriate method. For example, see
    :meth:`RPCServer.eth_getBlockByHash`.
    '''

    module_classes = (
        Eth,
    )

    def __init__(self, chain):
        self.chain = chain
        self.modules = {}
        for m in self.module_classes:
            self.modules[m.__name__.lower()] = m(chain)

    def _lookup_method(self, rpc_method):
        method_pieces = rpc_method.split('_')

        if len(method_pieces) != 2:
            # This check provides a security guarantee: that it's impossible to invoke
            # a method with an underscore in it. Only public methods on the modules
            # will be callable by external clients.
            raise ValueError("Invalid RPC method: %r" % rpc_method)
        module_name, method_name = method_pieces

        if module_name not in self.modules:
            raise ValueError("Module unavailable: %r" % module_name)
        module = self.modules[module_name]

        try:
            return getattr(module, method_name)
        except AttributeError:
            raise ValueError("Method not implemented: %r" % rpc_method)

    def execute(self, request):
        '''
        The key entry point for all incoming requests
        '''
        response = generate_response(request)

        try:
            if request.get('jsonrpc', None) != '2.0':
                raise NotImplementedError("Only the 2.0 jsonrpc protocol is supported")

            method = self._lookup_method(request['method'])
            response['result'] = method(*request['params'])
        except ValueError as exc:
            response['error'] = str(exc)
        except NotImplementedError as exc:
            response['error'] = "Method not implemented: %r" % request['method']
            custom_message = str(exc)
            if custom_message:
                response['error'] += ' - %s' % custom_message

        return json.dumps(response)