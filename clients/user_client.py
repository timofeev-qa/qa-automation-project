import uuid
from datetime import datetime, timedelta, UTC
from service.service_core import (
    svc_create_user,
    svc_create_token,
    svc_get_all_users,
    svc_get_user_by_id,
    svc_get_user_by_username,
    svc_get_user_by_email,
    svc_get_token_by_user_id,
    svc_update_user_by_id,
    svc_delete_user_by_id
)


class UserClient():
    def __init__(self, db_client):
        self.client = db_client

    def cli_build_user_payload(self, **overrides):
        payload = {
            "user_name": f"user_{uuid.uuid4().hex[:8]}",
            "user_email": f"e{uuid.uuid4().hex[:8]}@example.com",
            "user_status": "inactive"
        }
        payload.update(overrides)
        for field, value in payload.items():
            if isinstance(value, str):
                payload[field] = value.lower()
        return payload
    
    def cli_build_token_payload(self):
        payload = {
            "token_value": f"{uuid.uuid4().hex}",
            "token_expires_at": f"{(datetime.now(UTC) + timedelta(days=1)).isoformat()}"
        }
        return payload
    
    def cli_create_random_inactive_user(self, **overrides):
        user_payload = self.cli_build_user_payload(**overrides)
        user_id = svc_create_user(user_payload)

        token_payload = self.cli_build_token_payload()
        svc_create_token(user_id, token_payload)

        return user_id

    def cli_get_users(self):
        return svc_get_all_users()
    
    def cli_get_user_by_id(self, user_id):
        return svc_get_user_by_id(user_id)
    
    def cli_get_user_by_username(self, user_name):
        return svc_get_user_by_username(user_name)
    
    def cli_get_user_by_email(self, user_email):
        return svc_get_user_by_email(user_email)
    
    def cli_get_user_token(self, user_id):
        return svc_get_token_by_user_id(user_id)

    def cli_update_user_by_id(self, user_token, user_id, payload):
        return svc_update_user_by_id(user_token, user_id, payload)

    def cli_delete_user_by_id(self, user_token, user_id):
        return svc_delete_user_by_id(user_token, user_id)
