from db.queries import (
    create_user,
    create_token,
    create_task,
    get_users,
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    get_token_by_user,
    get_task_by_id,
    get_task_by_id,
    get_tasks_by_user,
    get_active_tasks_by_user,
    update_user_by_id,
    update_task_by_id,
    delete_user_by_id
)
from service.service_validations import (
    validate_user_for_create,
    validate_user_for_update,
    validate_user_token,
    validate_user_is_active,
    validate_user_name_existance,
    validate_user_email_existance,
    validate_task_for_create,
    validate_task_for_update,
    validate_key_existance,
    validate_task_is_done,
    return_search_key_is_active,
    validate_token_is_linked_to_user
)


# create
# create user
def svc_create_user(payload):
    validate_user_for_create(payload)
    return create_user(payload)

# create token
def svc_create_token(user_id, payload):
    validate_key_existance(user_id)
    create_token(user_id, payload)

# create task
def svc_create_task(user_token, payload):
    validate_task_for_create(payload)
    validate_user_token(user_token, payload)
    validate_user_is_active(payload["user_id"])
    return create_task(payload)

# get
# get users
def svc_get_all_users():
    result = get_users()

    if result:
        return result
    
    raise ValueError("users list is empty")

def svc_get_user_by_id(user_id):
    validate_key_existance(user_id)
    return get_user_by_id(user_id)

def svc_get_user_by_username(user_name):
    validate_user_name_existance(user_name)
    return get_user_by_username(user_name)

def svc_get_user_by_email(user_email):
    validate_user_email_existance(user_email)
    return get_user_by_email(user_email)

# get tokens
def svc_get_token_by_user_id(user_id):
    validate_key_existance(user_id)
    return get_token_by_user(user_id)

# get tasks
def svc_get_tasks_by_user_id(user_id, is_active=None):
    validate_key_existance(user_id)
    if return_search_key_is_active(is_active):
        result = get_active_tasks_by_user(user_id)
    else:
        result = get_tasks_by_user(user_id)

    if result:
        return result
    
    raise ValueError("tasks list is empty")

def svc_get_task_by_id(task_id):
    validate_key_existance(task_id)
    return get_task_by_id(task_id)

# update
# update user
def svc_update_user_by_id(user_token, user_id, payload):
    validate_key_existance(user_id)
    validate_user_for_update(payload)
    validate_token_is_linked_to_user(user_token, user_id)
    return update_user_by_id(user_id, payload)

# update task
def svc_update_task_by_id(user_token, task_id, user_id, payload):
    validate_key_existance(task_id)
    validate_task_for_update(payload)
    validate_token_is_linked_to_user(user_token, user_id)
    validate_task_is_done(task_id, payload)
    validate_user_is_active(user_id)
    return update_task_by_id(task_id, payload)

# delete
# delete user
def svc_delete_user_by_id(user_token, user_id):
    validate_key_existance(user_id)
    validate_user_token(user_token, {"user_id": user_id})
    return delete_user_by_id(user_id)