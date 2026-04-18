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
    return user_client.cli_create_random_inactive_user()

@pytest.fixture
def authorized_active_user_id(user_client):
    return user_client.cli_create_random_inactive_user(user_status="active")