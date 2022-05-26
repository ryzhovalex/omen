from flask import url_for
from werkzeug.security import check_password_hash as from_hash
from werkzeug.security import generate_password_hash as to_hash
from puft import Puft, Database

from src.app.user.user import User
from src.app.post.post import Post


def import_std():
    """Import standard instances for testing."""
    puft = Puft.instance()
    db = Database.instance()
    # Create test request context for the app
    ctx = puft.test_request_context()
    return {
        "puft": puft, "db": db, "ctx": ctx, "url_for": url_for,
        "to_hash": to_hash, "from_hash": from_hash
    }


def import_main():
    return {'User': User, 'Post': Post}
