import pytest
from helpers.asserts import (
    assert_item_matches_payload
)


# P0
def test_create_get_tasks_for_active_user_scenario(authorized_active_user_id, user_client, task_client):
    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_active_user_id))

    # creating tasks
    first_task_payload = task_client.cli_build_task_payload(authorized_active_user_id)
    first_task_id = task_client.cli_create_inactive_task_for_active_user(
        user_token=token["token_value"],
        user_id=authorized_active_user_id,
        task_title=first_task_payload["task_title"],
        task_description=first_task_payload["task_description"],
        task_status=first_task_payload["task_status"]
    )

    second_task_payload = task_client.cli_build_task_payload(authorized_active_user_id)
    second_task_id = task_client.cli_create_inactive_task_for_active_user(
        user_token=token["token_value"],
        user_id=authorized_active_user_id,
        task_title=second_task_payload["task_title"],
        task_description=second_task_payload["task_description"],
        task_status=second_task_payload["task_status"]
    )

    third_task_payload = task_client.cli_build_task_payload(authorized_active_user_id)
    third_task_id = task_client.cli_create_inactive_task_for_active_user(
        user_token=token["token_value"],
        user_id=authorized_active_user_id,
        task_title=third_task_payload["task_title"],
        task_description=third_task_payload["task_description"],
        task_status=third_task_payload["task_status"]
    )

    # getting tasks
    first_task = dict(task_client.cli_get_task_by_id(first_task_id))
    second_task = dict(task_client.cli_get_task_by_id(second_task_id))
    third_task = dict(task_client.cli_get_task_by_id(third_task_id))
    
    user_tasks_list = list(task_client.cli_get_tasks_by_user(authorized_active_user_id))
    user_tasks = []
    for item in user_tasks_list:
        user_tasks.append(dict(item))

    # validating tasks
    assert authorized_active_user_id == first_task["user_id"], "user_id does not match"
    assert_item_matches_payload(first_task, first_task_payload)

    assert authorized_active_user_id == second_task["user_id"], "user_id does not match"
    assert_item_matches_payload(second_task, second_task_payload)

    assert authorized_active_user_id == third_task["user_id"], "user_id does not match"
    assert_item_matches_payload(third_task, third_task_payload)

    for task in user_tasks:
        assert authorized_active_user_id == task["user_id"], "user_id does not match"
    
    assert len(user_tasks) == 3, "user has 3 tasks"

def test_create_task_for_inactive_user(authorized_user_id, user_client, task_client):
    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_user_id))

    # creating task
    with pytest.raises(ValueError) as exc:
        task_id = task_client.cli_create_inactive_task_for_active_user(
            user_token=token["token_value"],
            user_id=authorized_user_id
        )
    assert "user" in str(exc.value) and "must be active for creating a task for them" in str(exc.value), "error message does not match"

def test_create_update_task_status_scenario(authorized_active_user_id, user_client, task_client):
    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_active_user_id))

    # creating task
    task_id = task_client.cli_create_inactive_task_for_active_user(
        user_token=token["token_value"],
        user_id=authorized_active_user_id
    )

    # updating task
    payload = {
        "task_status": "active"
    }
    updated_task = task_client.cli_update_task_by_id(
        user_token=token["token_value"],
        task_id=task_id,
        user_id=authorized_active_user_id,
        payload=payload
    )

    # validating task
    assert task_id == updated_task["task_id"], "task_id does not match"
    assert authorized_active_user_id == updated_task["user_id"], "user_id does not match"
    assert "active" == updated_task["task_status"], "task_status does not match"

def test_validate_restrictions_for_task_with_status_done(authorized_active_user_id, user_client, task_client):
    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_active_user_id))

    # creating task
    task_id = task_client.cli_create_inactive_task_for_active_user(
        user_token=token["token_value"],
        user_id=authorized_active_user_id,
        task_status="done"
    )

    # updating task
    payload = {
        "task_title": "changed.title",
        "task_description": "changed description",
        "task_status": "active"
    }
    with pytest.raises(ValueError) as exc:
        updated_task = task_client.cli_update_task_by_id(
            user_token=token["token_value"],
            task_id=task_id,
            user_id=authorized_active_user_id,
            payload=payload
        )
    assert "cannot modify done task except for task_description" in str(exc.value), "error message does not match"

    # validating task wasn't changed
    task = dict(task_client.cli_get_task_by_id(task_id))
    assert payload["task_description"] != task["task_description"], "task_description changes should not apply because some other fields are invalid for changes"
    assert "done" == task["task_status"], "task_status does not match"

    # changing task's description only
    payload = {
        "task_description": "changed description"
    }
    updated_task = dict(task_client.cli_update_task_by_id(
        user_token=token["token_value"],
        task_id=task_id,
        user_id=authorized_active_user_id,
        payload=payload
    ))
    
    # validating task's description is changed
    assert authorized_active_user_id == updated_task["user_id"], "user_id does not match"
    assert task_id == updated_task["task_id"], "task_id does not match"
    assert payload["task_description"] == updated_task["task_description"], "task_description does not match"
