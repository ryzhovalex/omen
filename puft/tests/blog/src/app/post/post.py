from puft import orm

from src.app.user.user import User


class Post(orm.Model):
    __tablename__ = 'post'

    id = orm.column(orm.integer, primary_key=True)
    title = orm.column(orm.string(150))
    dscr = orm.column(orm.text)
    user_id = orm.column(orm.integer, orm.foreign_key(User.id))
