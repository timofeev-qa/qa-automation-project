from db.queries import (
    get_user_by_id,
    get_task_by_id,
    get_token_by_user,
    get_active_tasks_by_user
)


ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789_"
ACTIVE_TASK_LIMIT = 3


# user validation
def validate_user_for_create(payload):
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")
    
    required_fields = ["user_name", "user_email", "user_status"]

    for field in required_fields:
        if field not in payload:
            raise ValueError(f"{field} is required")
        
    for field in payload:
        if field not in required_fields:
            raise ValueError(f"unexpected field: {field}")
    
    validate_user_name(payload["user_name"])
    validate_user_email(payload["user_email"])
    validate_user_status(payload["user_status"])

def validate_user_for_update(payload):
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")
    
    allowed_fields = ["user_name", "user_email", "user_status"]
    field_parts = []

    for field in allowed_fields:
        if field in payload:
            field_parts.append(field)
    
    if not field_parts:
        raise ValueError("payload is empty")
        
    for field in payload:
        if field not in allowed_fields:
            raise ValueError(f"unexpected field: {field}")
    
    if "user_name" in payload:
        validate_user_name(payload["user_name"])
    if "user_email" in payload:
        validate_user_email(payload["user_email"])
    if "user_status" in payload:
        validate_user_status(payload["user_status"])

def validate_user_name(username):
    if not 2 <= len(username) <= 32:
        raise ValueError("username lenght must be from 2 to 32 characters")
    
    for char in username:
        if char not in ALLOWED_CHARS:
            raise ValueError("username must only contain letters and digits")
        
    if not username[0].isalpha():
        raise ValueError("username must start with letter")
    
def validate_user_email(email):
    if len(email) == 0:
        raise ValueError("email is empty")

    if email.count("@") != 1:
        raise ValueError("incorrect email structure")

    local, domain = email.split("@")

    if len(local) == 0 or len(domain) == 0:
        raise ValueError("incorrect email structure")

    if domain.count(".") != 1:
        raise ValueError("incorrect email structure")

    if domain[0] == "." or domain[-1] == ".":
        raise ValueError("incorrect email structure")

    for char in local:
        if char not in ALLOWED_CHARS:
            raise ValueError("email local part must only contain letters and digits")
        
    if not local[0].isalpha():
        raise ValueError("email local part must start with letter")
    
    for char in domain:
        if char not in ALLOWED_CHARS and char != ".":
            raise ValueError("domain must only contain letters, digits and dot")

def validate_user_status(status):
    if status not in ("active", "inactive"):
        raise ValueError("user's status can only be active or inactive")

def validate_user_name_exists(user_name):
    if user_name in (None, "", " "):
        raise ValueError("user_name is empty")

def validate_user_email_exists(user_email):
    if user_email in (None, "", " "):
        raise ValueError("user_email is empty")

def validate_user_exists(user_id):
    fetched_user = get_user_by_id(user_id)

    if not fetched_user:
        raise ValueError(f"user not found")

def validate_user_is_active(user_id):
    fetched_user = get_user_by_id(user_id)

    if not fetched_user:
        raise ValueError(f"user not found")
    
    if fetched_user["user_status"] == "inactive":
        raise ValueError(f"user {fetched_user} must be active for creating a task for them")

# token validation
def validate_user_token(user_token, payload):
    validate_token_is_linked_to_user(user_token, payload["user_id"])

def validate_token_is_linked_to_user(actual_token, user_id):
    if not actual_token:
        raise PermissionError("access denied: user_token is empty")
    
    if actual_token in (None, "", " "):
        raise PermissionError("access denied: user_token is empty")
    
    validate_user_exists(user_id)

    expected_token = dict(get_token_by_user(user_id))
    if expected_token["token_value"] != actual_token:
        raise PermissionError(f"access denied: wrong access token '{actual_token}'")

# task validation
def validate_task_for_create(payload):

    if not isinstance(payload, dict):
        raise ValueError("task's payload must be a dict")

    required_fields = ["user_id", "task_title", "task_description", "task_status"]

    for field in required_fields:
        if field not in payload:
            raise ValueError(f"{field} is required")
        
    for field in payload:
        if field not in required_fields:
            raise ValueError(f"unexpected field: {field}")

    if payload["user_id"] in (None, "", " "):
        raise ValueError(f"field user_id has an empty value '{payload["user_id"]}'")
    
    validate_task_title(payload["task_title"])
    validate_task_status(payload["task_status"])

def validate_task_for_update(payload):
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")
    
    allowed_fields = ["task_title", "task_description", "task_status"]
    field_parts = []

    for field in allowed_fields:
        if field in payload:
            field_parts.append(field)
    
    if not field_parts:
        raise ValueError("payload is empty")
        
    for field in payload:
        if field not in allowed_fields:
            raise ValueError(f"unexpected field: {field}")
    
    if "task_title" in payload:
        validate_task_title(payload["task_title"])
    if "task_status" in payload:
        validate_task_status(payload["task_status"])

def validate_task_title(title):
    if not 2 <= len(title) <= 32:
        raise ValueError("task's title lenght must be from 2 to 32 characters")
    
    for char in title:
        if char not in ALLOWED_CHARS and char != ".":
            raise ValueError("task's title must only contain letters, digits and dot")
        
    if not title[0].isalpha():
        raise ValueError("task's title must start with letter")

def validate_task_status(status):
    if status not in ("done", "active", "inactive"):
        raise ValueError("task's status can only be active, inactive or done")

def validate_task_is_done(task_id, payload):
    fetched_task = get_task_by_id(task_id)

    if not fetched_task:
        raise ValueError(f"task not found")
    
    has_other_fields = any(k != "task_description" for k in payload)

    if fetched_task["task_status"] == "done" and has_other_fields:
        raise ValueError("cannot modify done task except for task_description")

def validate_key_presence(key):
    if key in (None, "", " "):
        raise ValueError(f"{key} is empty")
    
def validate_task_exists(task):
    if not task:
        raise ValueError("task not found")

def resolve_active_task_filter(is_active=None):
    if is_active is None:
        return False
    elif isinstance(is_active, str) and is_active.lower() == "active":
        return True
    else:
        raise ValueError("is_active must be 'active' or None")

def validate_task_payload_is_instance(payload):
    if not isinstance(payload, dict):
        raise ValueError("task's payload must be a dict")

def validate_tasks_limit_for_create(user_id, task_payload):
    validate_key_presence(user_id)
    validate_task_payload_is_instance(task_payload)

    if "task_status" in task_payload:
        if "active" == task_payload["task_status"]:
            count_tasks = len(list(get_active_tasks_by_user(user_id)))
            if count_tasks >= ACTIVE_TASK_LIMIT:
                raise ValueError(f"adding additional active task will exceed user's active tasks limit of: '{ACTIVE_TASK_LIMIT}'")
            
def validate_tasks_limit_for_update(user_id, task_id, task_payload):
    validate_key_presence(user_id)
    validate_key_presence(task_id)
    validate_task_payload_is_instance(task_payload)

    if "task_status" in task_payload:
        if "active" == task_payload["task_status"]:
            count_tasks = len(list(get_active_tasks_by_user(user_id)))
            pre_updated_task = get_task_by_id(task_id)

            if count_tasks >= ACTIVE_TASK_LIMIT and pre_updated_task["task_status"] != "active":
                raise ValueError(f"updating this task will exceed user's active tasks limit of: '{ACTIVE_TASK_LIMIT}'")
            