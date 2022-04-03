from puft.constants.orm_types import *


class User(Model):
    """Basic user of the system."""
    __tablename__ = "user"

    id = column(integer, primary_key=True)
    username = column(string(50), nullable=False, unique=True)
    password = column(string(50), nullable=False)
    firstname = column(string(80), default="Michael")
    # surname = column(string(80), default="Jackson")
