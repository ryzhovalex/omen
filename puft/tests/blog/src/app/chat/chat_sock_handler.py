from puft import SockHandler, log


class ChatSockHandler(SockHandler):
    def on_message(self, message):
        return {'message': {
            'user_author_id': 1,
            'content': 'Welcome to the chat!'
        }}
