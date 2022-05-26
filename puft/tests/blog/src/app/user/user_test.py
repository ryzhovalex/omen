from src.app.user.user_view import UserView


class TestUser():
    def test_structure(self, client):
        data = client.get('/user/1').json
        assert 'post_ids' in data
        assert 'username' in data
