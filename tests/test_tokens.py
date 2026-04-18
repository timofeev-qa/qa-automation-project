import pytest

# P0
def test_update_delete_user_with_token_scenario(authorized_user_id, user_client):
    # fetching user token
    token = dict(user_client.cli_get_user_token(authorized_user_id))

    # building update payload
    updated_payload = {
        "user_status": "active"
    }

    # updating user
    updated_user = dict(user_client.cli_update_user_by_id(
        user_token=token["token_value"],
        user_id=authorized_user_id,
        payload=updated_payload
    ))
    
    # validating user
    assert authorized_user_id == updated_user["user_id"], "user_id does not match"
    assert updated_payload["user_status"] == updated_user["user_status"], "user_status does not match"

    # deleting user
    response = user_client.cli_delete_user_by_id(
        user_token=token["token_value"],
        user_id=authorized_user_id
    )

    # validating deletion
    assert 0 < response, "user should be deleted"

    user = user_client.cli_get_user_by_id(authorized_user_id)
    assert not user, "user should not existed"

def test_update_delete_user_without_token_scenario(authorized_user_id, user_client):
    # building update payload
    updated_payload = {
        "user_status": "active"
    }

    # updating user
    with pytest.raises(PermissionError) as token_is_empty_exc:
        user = dict(user_client.cli_update_user_by_id(
            user_token=None,
            user_id=authorized_user_id,
            payload=updated_payload
        ))
    assert "access denied: user_token is empty" in str(token_is_empty_exc.value), "error message does not match"

    # deleting user
    with pytest.raises(PermissionError) as token_is_invalid_exc:
        response = user_client.cli_delete_user_by_id(
            user_token=None,
            user_id=authorized_user_id
        )
    assert "access denied: user_token is empty" in str(token_is_invalid_exc.value), "error message does not match"

def test_update_delete_user_with_wrong_token_scenario(authorized_user_id, user_client):
    # building update payload
    updated_payload = {
        "user_status": "active"
    }

    # updating user
    with pytest.raises(PermissionError) as token_is_empty_exc:
        user = dict(user_client.cli_update_user_by_id(
            user_token="wrong_token_value",
            user_id=authorized_user_id,
            payload=updated_payload
        ))
    assert "access denied: wrong access token" in str(token_is_empty_exc.value), "error message does not match"

    # deleting user
    with pytest.raises(PermissionError) as token_is_invalid_exc:
        response = user_client.cli_delete_user_by_id(
            user_token="wrong_token_value",
            user_id=authorized_user_id
        )
    assert "access denied: wrong access token" in str(token_is_invalid_exc.value), "error message does not match"
