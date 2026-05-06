import uuid
from service.service_core import (
    svc_create_task,
    svc_get_task_by_id,
    svc_get_tasks_by_user_id,
    svc_update_task_by_id
)


class TaskClient():
    def __init__(self, db_client):
        self.client = db_client
        
    def cli_build_task_payload(self, user_id, **overrides):
        payload = {
            "user_id": user_id,
            "task_title": f"task.title.{uuid.uuid4().hex[:8]}",
            "task_description": f"task description {uuid.uuid4().hex[:8]}",
            "task_status": "inactive"
        }
        payload.update(overrides)
        for field, value in payload.items():
            if isinstance(value, str):
                payload[field] = value.lower()
        return payload

    def cli_create_task_for_active_user(self, user_token, user_id, **overrides):
        payload = self.cli_build_task_payload(user_id, **overrides)
        return svc_create_task(user_token, payload)
    
    def cli_get_task_by_id(self, task_id):
        return svc_get_task_by_id(task_id)        

    def cli_get_tasks_by_user(self, user_id, is_active=None):
        return svc_get_tasks_by_user_id(user_id, is_active)
        
    def cli_update_task_by_id(self, user_token, task_id, user_id, payload):
        return svc_update_task_by_id(user_token, task_id, user_id, payload)
