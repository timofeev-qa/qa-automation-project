import pytest
from helpers.asserts import (
    assert_item_matches_payload
)
from service.service_validations import ACTIVE_TASK_LIMIT


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

def test_validate_restrictions_for_user_to_have_active_tasks_exceeded_active_tasks_limit(authorized_active_user_id, user_client, task_client):
    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_active_user_id))

    # creating active & inactive tasks

    inactive_task_id = task_client.cli_create_inactive_task_for_active_user(
        user_token=token["token_value"],
        user_id=authorized_active_user_id
    )

    for _ in range (ACTIVE_TASK_LIMIT):
        task_client.cli_create_inactive_task_for_active_user(
            user_token=token["token_value"],
            user_id=authorized_active_user_id,
            task_status="active"
        )

    # validating user has active tasks matches ACTIVE_TASK_LIMIT const
    user_active_tasks = list(task_client.cli_get_tasks_by_user(authorized_active_user_id, "active"))
    count_tasks = len(user_active_tasks)
    assert ACTIVE_TASK_LIMIT == count_tasks, f"expected '{ACTIVE_TASK_LIMIT}' active tasks created, actual active tasks created: '{count_tasks}'"

    # creating one more active task
    with pytest.raises(ValueError) as exc:
        task_client.cli_create_inactive_task_for_active_user(
            user_token=token["token_value"],
            user_id=authorized_active_user_id,
            task_status="active"
        )
    assert f"adding additional active task will exceed user's active tasks limit of: '{ACTIVE_TASK_LIMIT}'" in str(exc.value)
    
    # validating user active tasks count does not change
    count_tasks_present = len(list(task_client.cli_get_tasks_by_user(authorized_active_user_id, "active")))
    assert count_tasks == count_tasks_present, f"expected active tasks count to stay {count_tasks}, got {count_tasks_present}"

    # updating status of inactive task to status=active
    payload = {
        "task_status": "active"
    }
    with pytest.raises(ValueError) as exc:
        task_client.cli_update_task_by_id(
            user_token=token["token_value"],
            task_id=inactive_task_id,
            user_id=authorized_active_user_id,
            payload=payload
        )
    assert f"updating this task will exceed user's active tasks limit of: '{ACTIVE_TASK_LIMIT}'" in str(exc.value)

    # validating user active tasks count does not change
    count_tasks_present = len(list(task_client.cli_get_tasks_by_user(authorized_active_user_id, "active")))
    assert count_tasks == count_tasks_present, f"expected active tasks count to stay {count_tasks}, got {count_tasks_present}"

def test_validate_completing_active_task_make_room_for_another_active_task(authorized_active_user_id, user_client, task_client):
    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_active_user_id))

    # creating active tasks
    active_task_id = task_client.cli_create_inactive_task_for_active_user(
        user_token=token["token_value"],
        user_id=authorized_active_user_id,
        task_status="active"
    )

    for _ in range (ACTIVE_TASK_LIMIT - 1):
        task_client.cli_create_inactive_task_for_active_user(
            user_token=token["token_value"],
            user_id=authorized_active_user_id,
            task_status="active"
        )

    # validating user has active tasks matches ACTIVE_TASK_LIMIT const
    user_active_tasks = list(task_client.cli_get_tasks_by_user(authorized_active_user_id, "active"))
    count_tasks = len(user_active_tasks)
    assert ACTIVE_TASK_LIMIT == count_tasks, f"expected active tasks count to stay {ACTIVE_TASK_LIMIT}, got {count_tasks}"

    # creating one more active task
    with pytest.raises(ValueError) as exc:
        task_client.cli_create_inactive_task_for_active_user(
            user_token=token["token_value"],
            user_id=authorized_active_user_id,
            task_status="active"
        )
    assert f"adding additional active task will exceed user's active tasks limit of: '{ACTIVE_TASK_LIMIT}'" in str(exc.value)
    
    # validating user active tasks count does not change
    count_tasks_present = len(list(task_client.cli_get_tasks_by_user(authorized_active_user_id, "active")))
    assert count_tasks == count_tasks_present, f"expected '{count_tasks}' active tasks created, actual active tasks created: '{count_tasks_present}'"

    # updating status of active task to status=done
    payload = {
        "task_status": "done"
    }
    task_client.cli_update_task_by_id(
        user_token=token["token_value"],
        task_id=active_task_id,
        user_id=authorized_active_user_id,
        payload=payload
    )

    # validating user active tasks count does change
    count_tasks_present0 = len(list(task_client.cli_get_tasks_by_user(authorized_active_user_id, "active")))
    assert count_tasks_present0 == count_tasks - 1, f"expected active tasks count to become {count_tasks - 1}, got {count_tasks_present0}"

    # create an active task
    active_task_id = task_client.cli_create_inactive_task_for_active_user(
        user_token=token["token_value"],
        user_id=authorized_active_user_id,
        task_status="active"
    )

    # validating the active task is created by user
    active_task = dict(task_client.cli_get_task_by_id(active_task_id))
    assert authorized_active_user_id == active_task["user_id"], "user_id does not match"

# P1
def test_validate_active_task_limit_does_not_restrict_from_creating_inactive_task(authorized_active_user_id, user_client, task_client):
    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_active_user_id))

    # creating active tasks
    for _ in range (ACTIVE_TASK_LIMIT):
        task_client.cli_create_inactive_task_for_active_user(
            user_token=token["token_value"],
            user_id=authorized_active_user_id,
            task_status="active"
        )

    # validating user has active tasks matches ACTIVE_TASK_LIMIT const
    user_active_tasks = list(task_client.cli_get_tasks_by_user(authorized_active_user_id, "active"))
    count_tasks = len(user_active_tasks)
    assert ACTIVE_TASK_LIMIT == count_tasks, f"expected '{ACTIVE_TASK_LIMIT}' active tasks created, actual active tasks created: '{count_tasks}'"

    # creating an inactive task
    task_client.cli_create_inactive_task_for_active_user(
        user_token=token["token_value"],
        user_id=authorized_active_user_id
    )

    # validating user has total tasks more than ACTIVE_TASK_LIMIT const and active tasks do not changed
    count_tasks_present = len(list(task_client.cli_get_tasks_by_user(authorized_active_user_id)))
    count_active_tasks = len(list(task_client.cli_get_tasks_by_user(authorized_active_user_id, "active")))

    assert count_active_tasks == ACTIVE_TASK_LIMIT, f"active tasks should not be changed"
    assert count_tasks_present == ACTIVE_TASK_LIMIT + 1, f"ACTIVE_TASK_LIMIT: '{ACTIVE_TASK_LIMIT}' should be lesser than total tasks count: '{count_tasks}'"

def test_validate_active_task_limit_does_not_restrict_from_updating_active_task(authorized_active_user_id, user_client, task_client):
    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_active_user_id))

    # creating active tasks
    for _ in range (ACTIVE_TASK_LIMIT):
        task_client.cli_create_inactive_task_for_active_user(
            user_token=token["token_value"],
            user_id=authorized_active_user_id,
            task_status="active"
        )

    # validating user has active tasks matches ACTIVE_TASK_LIMIT const
    user_active_tasks = list(task_client.cli_get_tasks_by_user(authorized_active_user_id, "active"))
    count_tasks = len(user_active_tasks)
    assert ACTIVE_TASK_LIMIT == count_tasks, f"expected '{ACTIVE_TASK_LIMIT}' active tasks created, actual active tasks created: '{count_tasks}'"

    pre_updated_task = dict(task_client.cli_get_task_by_id(user_active_tasks[0]["task_id"]))

    # updating an active task
    payload = {
        "task_description": "updated task description",
        "task_status": "active"
    }
    task_client.cli_update_task_by_id(
        user_token=token["token_value"],
        task_id=user_active_tasks[0]["task_id"],
        user_id=authorized_active_user_id,
        payload=payload
    )

    # validating task update
    post_updated_task = dict(task_client.cli_get_task_by_id(user_active_tasks[0]["task_id"]))
    assert "updated task description" == post_updated_task["task_description"], "task description was not updated"
    assert "active" == post_updated_task["task_status"], "task status should stay active"

    # validating task active count does not changed
    count_tasks_present = len(list(task_client.cli_get_tasks_by_user(authorized_active_user_id, "active")))
    assert count_tasks_present == ACTIVE_TASK_LIMIT, f"expected active tasks count to stay {ACTIVE_TASK_LIMIT}, got {count_tasks_present}"
