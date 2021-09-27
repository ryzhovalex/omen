from typing import Any, List, Dict, Tuple, Callable

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .domain import Domain
from ...helpers.logger import logger
from ...helpers.constants import Path
from ...tools.stdkit import format_error_message


# Here database variable are referenced at top layer to be visible for ORMs.
# It is kinda messy, and in future it may be refactored (nothing more permanent than temporary).
db = SQLAlchemy()


class Database(Domain):
    """Utilizes SQLAlchemy database operations."""
    def __init__(self):
        self.db = db
        self.migrate = None

    def setup_db(self, flask_app: Flask, db_uri: Path) -> None:
        """Setup database and migration object with given Flask app."""
        logger.info(f"Set database path: {db_uri}")
        flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
        flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Supress warning.
        self.db.init_app(flask_app)
        self.migrate = Migrate(flask_app, self.db)

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
            error_message = format_error_message("Migrate object hasn't implemented yet.")
            raise AttributeError(error_message)

    def create_all(self) -> None:
        self.db.create_all()

    def drop_all(self):
        self.db.drop_all()

    def add(self, entity):
        """Place an object in the session."""
        self.db.session.add(entity)

    def commit(self):
        """Commit current transaction."""
        self.db.session.commit()

    def rollback(self):
        self.db.session.rollback()

    def remove(self):
        self.db.session.remove()