from puft.constants.orm_types import (
    Model, boolean, integer, string, text, backref, relationship, column
)


class User(Model):
    __tablename__ = 'user'

    id = column(integer, primary_key=True)
    username = column(string(150))
    password = column(string(150))
    posts = relationship('Post', backref='user', foreign_keys='[Post.user_id]')
