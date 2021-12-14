import os

from flask import Flask
from loguru import logger


def create_app():
    app = Flask(__name__)
    logger.debug(os.environ["PUFT_ROOT_DIR"])
    @app.route("/raise")
    def raise_err():
        raise_test()
    return app

@logger.catch
def raise_test():
    raise ValueError("YOU SHALL NOT PASS")