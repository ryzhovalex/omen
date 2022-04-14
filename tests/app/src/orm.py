from puft.constants.orm_types import *


# Joined table inheritance
# https://docs.sqlalchemy.org/en/14/orm/inheritance.html#joined-table-inheritance
# https://docs.sqlalchemy.org/en/14/orm/inheritance.html#relationships-with-joined-inheritance
# https://stackoverflow.com/questions/2859339/is-multi-level-polymorphism-possible-in-sqlalchemy
# https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/inheritance.html
# Fix AmbiguousForeignKeysError for relationships between two children
# https://stackoverflow.com/questions/22355890/sqlalchemy-multiple-foreign-keys-in-one-mapped-class-to-the-same-primary-key
# Support multiple relationships for children in one inheritance tree
# https://stackoverflow.com/questions/54703652/sqlalchemy-multiple-relationships-between-tables
class Base(Model):
    __tablename__ = "base"

    id = column(integer, primary_key=True)
    type = column(string(50))

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "base"
    }


class Message(Base):
    __tablename__ = "message"

    id = column(integer, foreign_key("base.id"), primary_key=True)
    title = column(string(50))
    content = column(text)

    user_id = column(foreign_key("user.id"))
    user = relationship("User", back_populates="messages", foreign_keys=[user_id])

    __mapper_args__ = {
        "polymorphic_identity": "message"
    }


class User(Base):
    """Basic user of the system."""
    __tablename__ = "user"

    id = column(integer, foreign_key("base.id"), primary_key=True)
    username = column(string(50), nullable=False, unique=True)
    password = column(string(50), nullable=False)
    firstname = column(string(80), default="Michael")
    surname = column(string(80), default="Jackson")

    messages = relationship("Message", back_populates="user", foreign_keys="[Message.user_id]")

    __mapper_args__ = {
        "polymorphic_identity": "user"
    }


class Admin(User):
    __tablename__ = "admin"

    id = column(integer, foreign_key("user.id"), primary_key=True)
    banned = column(integer)

    __mapper_args__ = {
        "polymorphic_identity": "admin"
    }
