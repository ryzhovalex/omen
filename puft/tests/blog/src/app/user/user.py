# from puft.orm_types import (
#     Model, boolean, integer, string, text, backref, relationship, column
# )
from puft import orm


class User(orm.Model):
    username = orm.column(orm.string(150))
    password = orm.column(orm.string(150))
    posts = orm.relationship('Post', backref='user', foreign_keys='[Post.user_id]')
