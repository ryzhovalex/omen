from functools import wraps
from typing import Callable

from warepy import logger, format_message
from flask import Flask
import flask_migrate
from flask_sqlalchemy import SQLAlchemy

from .service import Service


# Here database variable are referenced at top layer to be visible for ORMs.
# It is kinda messy, and in future it may be refactored (nothing more permanent than temporary).
native_db = SQLAlchemy()


def migration_implemented(func: Callable):
    @wraps(func)
    def inner(self_instance, *args, **kwargs):
        if type(self_instance) is not Database:
            raise TypeError(
                format_message("Decorator migration_implemented cannot be applied to type {}.", type(self_instance))
            )
        elif not self_instance.migration:
            error_message = format_message("Migrate object hasn't been implemented yet.")
            raise AttributeError(error_message)
        else:
            return func(self_instance, *args, **kwargs)
    return inner


class Database(Service):
    """Operates over Database processes."""
    def __init__(self, service_config: dict) -> None:
        super().__init__(service_config)
        self.native_db = native_db
        # For now service config propagated to Database domain.
        self._assign_uri_from_config(service_config)

    @logger.catch
    def _assign_uri_from_config(self, config: dict) -> None:
        raw_uri = config.get("URI", None)  # type: str

        if not raw_uri:
            logger.info("URI for database not specified, using default sqlite3.")
        
        # Since URI from config is a raw path, need to calculate protocol.
        # Case 1: SQLite database.
        # TODO: Maybe instead of direct checking, create DatabaseTypeEnum?
        if "sqlite" in raw_uri or ".db" in raw_uri:
            # Set absolute path to db.
            # Source: https://stackoverflow.com/a/44687471/14748231.
            self.uri = "sqlite:///" + raw_uri

    @logger.catch
    @migration_implemented
    def init_migration(self, directory: str = "migrations", multidb: bool = False) -> None:
        """Initializes migration support for the application."""
        flask_migrate.init(directory=directory, multidb=multidb)

    @logger.catch
    @migration_implemented
    def migrate_migration(
        self,
        directory: str = "migrations", 
        message = None, 
        sql = False, 
        head: str = "head", 
        splice = False, 
        branch_label = None, 
        version_path = None, 
        rev_id = None
    ) -> None:
        flask_migrate.migrate(
            directory=directory,
            message=message,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id
        )

    @logger.catch
    @migration_implemented
    def upgrade_migration(
        self,
        directory: str = "migrations",
        revision: str = "head",
        sql = False,
        tag = None
    ) -> None:
        flask_migrate.upgrade(
            directory=directory,
            revision=revision,
            sql=sql,
            tag=tag
        )

    @logger.catch
    def setup(self, flask_app: Flask) -> None:
        """Setup database and migration object with given Flask app."""
        logger.info(f"Set database path: {self.uri}")
        flask_app.config["SQLALCHEMY_DATABASE_URI"] = self.uri
        flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Supress warning.
        self.native_db.init_app(flask_app)
        self.migration = flask_migrate.Migrate(flask_app, self.native_db)

    @logger.catch
    def get_native_db(self) -> SQLAlchemy:
        return self.native_db

    @logger.catch
    @migration_implemented
    def get_migration(self) -> flask_migrate.Migrate:
        """Return migration object.
        
        Raise:
            AttributeError: If Migrate object hasn't implemented yet."""
        return self.migration

    @logger.catch
    @migration_implemented
    def create_all_tables(self) -> None:
        self.native_db.create_all()

    @logger.catch
    @migration_implemented
    def drop_all_tables(self):
        "Drop all tables."
        self.native_db.drop_all()

    @logger.catch
    @migration_implemented
    def add_to_session(self, entity):
        """Place an object in the session."""
        self.native_db.session.add(entity)

    @logger.catch
    @migration_implemented
    def commit_session(self):
        """Commit current transaction."""
        self.native_db.session.commit()

    @logger.catch
    @migration_implemented
    def rollback_session(self):
        self.native_db.session.rollback()

    @logger.catch
    @migration_implemented
    def remove_session(self):
        self.native_db.session.remove()
