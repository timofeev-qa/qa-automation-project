from clients.db_client import DBClient
from clients.user_client import UserClient
from clients.task_client import TaskClient

import pytest


@pytest.fixture
def db_client():
    return DBClient()

@pytest.fixture
def user_client(db_client):
    return UserClient(db_client)

@pytest.fixture
def task_client(db_client):
    return TaskClient(db_client)

@pytest.fixture
def authorized_user_id(user_client):
    user_id = user_client.cli_create_random_inactive_user()
    token = dict(user_client.cli_get_user_token(user_id))
    try:
        yield user_id
    finally:
        user_client.cli_delete_user_by_id(
            user_token=token["token_value"],
            user_id=user_id)

@pytest.fixture
def authorized_active_user_id(user_client):
    active_user_id = user_client.cli_create_random_inactive_user(user_status="active")
    token = dict(user_client.cli_get_user_token(active_user_id))
    try:
        yield active_user_id
    finally:
        user_client.cli_delete_user_by_id(
            user_token=token["token_value"],
            user_id=active_user_id)