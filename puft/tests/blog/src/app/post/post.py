from puft.constants.orm_types import (
    Model, column, text, relationship, integer, string, foreign_key
)

from src.app.user.user import User


class Post(Model):
    __tablename__ = 'post'

    id = column(integer, primary_key=True)
    title = column(string(150))
    dscr = column(text)
    user_id = column(integer, foreign_key(User.id))
