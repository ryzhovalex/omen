from typing import Any, List, Dict, Tuple, Callable

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from warepy import logger, format_message

from .domain import Domain


# Here database variable are referenced at top layer to be visible for ORMs.
# It is kinda messy, and in future it may be refactored (nothing more permanent than temporary).
native_db = SQLAlchemy()


class Database(Domain):
    """Utilizes SQLAlchemy database operations."""
    @logger.catch
    def __init__(self, config: dict):
        self.db = native_db
        self.migrate = None
        try:
            raw_uri = config["URI"]  # type: str
        except KeyError:
            error_message = format_message("You must specify URI for database in config.")
            raise ValueError(error_message)
        
        # Since URI from config is a raw path, need to calculate protocol.
        # Case 1: SQLite database.
        if "sqlite" in raw_uri or ".db" in raw_uri:
            self.uri = "sqlite://" + raw_uri

    @logger.catch
    def setup_db(self, flask_app: Flask) -> None:
        """Setup database and migration object with given Flask app."""
        logger.info(f"Set database path: {self.uri}")
        flask_app.config["SQLALCHEMY_DATABASE_URI"] = self.uri
        flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Supress warning.
        self.db.init_app(flask_app)
        self.migrate = Migrate(flask_app, self.db)

    @logger.catch
    def get_db(self) -> SQLAlchemy:
        return self.db

    @logger.catch
    def get_migrate(self) -> Migrate:
        """Return Migrate object.
        
        Raise:
            AttributeError: If Migrate object hasn't implemented yet."""
        if self.migrate:
            return self.migrate
        else:
            error_message = format_message("Migrate object hasn't implemented yet.")
            raise AttributeError(error_message)

    @logger.catch
    def create_all(self) -> None:
        self.db.create_all()

    @logger.catch
    def drop_all(self):
        self.db.drop_all()

    @logger.catch
    def add(self, entity):
        """Place an object in the session."""
        self.db.session.add(entity)

    @logger.catch
    def commit(self):
        """Commit current transaction."""
        self.db.session.commit()

    @logger.catch
    def rollback(self):
        self.db.session.rollback()

    @logger.catch
    def remove(self):
        self.db.session.remove()