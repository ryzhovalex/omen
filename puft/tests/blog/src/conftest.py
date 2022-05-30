import pytest
from src.app.user.user_test import TestUser
from src.app.user.user import AdvancedUser, User
from puft import Puft, Db, get_root_path
from flask.testing import FlaskClient

from src.app.badge.badge_test import badge, badge_mock
from src.app.user.user_test import user, advanced_user_with_badge, user_mock
from src.app.post.post_test import post, post_mock
from src.app.post.tag.tag_test import tag, tag_mock, tags, tag_names
