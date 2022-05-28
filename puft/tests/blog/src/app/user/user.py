from puft import orm

from src.app.badge.badge import Badge


class User(orm.Model):
    type = orm.column(orm.string(50))
    username = orm.column(orm.string(150))
    password = orm.column(orm.string(150))
    posts = orm.relationship(
        'Post', backref='user', foreign_keys='[Post.user_id]')


class AdvancedUser(User):
    badge_id = orm.column(orm.integer, orm.foreign_key(Badge.id))
