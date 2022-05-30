from puft import Service, log, socket


class ChatSv(Service):
    @socket.on('connect')
    def connect(self):
        log.debug('Chat connect')
        socket.send('Connected')

    @socket.on('disconnect')
    def disconnect(self):
        log.debug('Chat disconnect')
        socket.send('Disconnected')

    @socket.on('message')
    def send_message(message):
        log.debug(f'Receive message {message}')
        socket.send(f'Message received: {message}')
