from puft import orm


class Tag(orm.Model):
    name = orm.column(orm.string(100))
