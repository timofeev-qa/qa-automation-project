

def assert_item_matches_payload(item, payload):
    for field, expected_value in payload.items():
        assert field in item, f"field '{field}' is missing in item"
        actual_value = item[field]
        assert actual_value == expected_value, (
            f"field '{field}' value '{actual_value}' does not match expected '{expected_value}'"
        )