import pytest
import sqlite3
from helpers.asserts import (
    assert_item_matches_payload
)


# P0
def test_create_get_user_scenario(user_client):
    # creating user
    payload = user_client.cli_build_user_payload()
    user_id = user_client.cli_create_random_inactive_user(**payload)
    
    # getting user
    user = dict(user_client.cli_get_user_by_id(user_id))

    # validating user
    assert_item_matches_payload(user, payload)
    
def test_update_user_status_scenario(authorized_user_id, user_client):
    # building payload
    payload = {
        "user_status": "active"
    }

    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_user_id))

    # updating user
    user = dict(user_client.cli_update_user_by_id(
        user_token=token["token_value"],
        user_id=authorized_user_id,
        payload=payload
    ))

    # validating user
    assert authorized_user_id == user["user_id"], "user_id does not match"
    assert "active" in user["user_status"], "user_status should be 'active'"

def test_delete_user_scenario(authorized_user_id, user_client):
    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_user_id))

    # deleting user
    response = user_client.cli_delete_user_by_id(
        user_token=token["token_value"], 
        user_id=authorized_user_id
    )

    # validating deletion
    assert 0 < response, "user should be deleted"

    user = user_client.cli_get_user_by_id(authorized_user_id)
    assert not user, "user should not existed"

# P1
def test_create_user_with_existed_email(user_client):
    # creating fist user
    first_payload = user_client.cli_build_user_payload()
    first_user_id = user_client.cli_create_random_inactive_user(**first_payload)

    # creating second user
    second_payload = {
        "user_name": f"up_{first_payload['user_name']}",
        "user_email": first_payload['user_email'],
        "user_status": "inactive"
    }
    with pytest.raises(sqlite3.IntegrityError) as exc:
        second_user_id = user_client.cli_create_random_inactive_user(**second_payload)
    assert "UNIQUE constraint failed" in str(exc.value), "error message does not match"
    assert "users.user_email" in str(exc.value), "error should reference users.user_email column"

    # validating first user doesn't change
    first_user = dict(user_client.cli_get_user_by_id(first_user_id))
    assert_item_matches_payload(first_user, first_payload)

def test_deleting_user_removes_all_associated_entities_scenario(authorized_active_user_id, user_client, task_client):
    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_active_user_id))

    # creating task
    task_id = task_client.cli_create_inactive_task_for_active_user(
        user_token=token["token_value"],
        user_id=authorized_active_user_id
    )

    # validating task
    task = task_client.cli_get_task_by_id(task_id)
    assert task_id == task["task_id"], "task_id does not match"

    # validating task and token are related to user
    assert authorized_active_user_id == task["user_id"], "user_id does not match"
    assert authorized_active_user_id == token["user_id"], "user_id does not match"

    # deleting user
    response = user_client.cli_delete_user_by_id(
        user_token=token["token_value"],
        user_id=authorized_active_user_id
    )

    # validating deletion
    assert 0 < response, "user should be deleted"

    user = user_client.cli_get_user_by_id(authorized_active_user_id)
    assert not user, "user should not existed"

    # validating associated entities deletion
    token = user_client.cli_get_user_token(authorized_active_user_id)
    assert not token, "token should not exist"
    with pytest.raises(ValueError) as tasks_are_empty_exc:
        tasks = task_client.cli_get_tasks_by_user(authorized_active_user_id)
    assert "tasks list is empty" in str(tasks_are_empty_exc.value)