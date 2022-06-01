from puft import Sock, log


class ChatSock(Sock):
    def on_message(self, message):
        return {'message': {
            'user_author_id': 1,
            'content': 'Welcome to the chat!'
        }}
