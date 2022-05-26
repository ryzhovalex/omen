from puft import View

from .user import User


class UserView(View):
    def get(self, id: int):
        user: User = User.query.filter_by(id=id).first()
        return {
            'username': user.username,
            'post_ids': [post.id for post in user.posts]
        }
