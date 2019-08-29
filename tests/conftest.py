from flask.testing import FlaskClient
from pytest import fixture
from typing import Callable, Iterator

from eNMS.database import Session
from eNMS.framework import create_app

import warnings


@fixture
def base_client() -> Iterator[FlaskClient]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        app = create_app("Test")
        app_context = app.app_context()
        app_context.push()
        Session.close()
        yield app.test_client()


@fixture
def user_client() -> Iterator[FlaskClient]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        app = create_app("Test")
        app_context = app.app_context()
        app_context.push()
        Session.close()
        client = app.test_client()
        with app.app_context():
            client.post(
                "/login",
                data={
                    "name": "admin",
                    "password": "admin",
                    "authentication_method": "Local User",
                },
            )
            yield client


def check_pages(*pages: str) -> Callable:
    def decorator(function: Callable) -> Callable:
        def wrapper(user_client: FlaskClient) -> None:
            function(user_client)
            for page in pages:
                r = user_client.get(page, follow_redirects=True)
                assert r.status_code == 200

        return wrapper

    return decorator
