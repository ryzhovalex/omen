from puft import Sock, log


class ChatSock(Sock):
    def on_connect(self):
        log.debug('Hehe connect')
    
    def on_send(self, data):
        log.debug(f'On send {data}')
        data = {'number': 4321}
        self.socket.send(data, namespace=self.namespace)
        return data
