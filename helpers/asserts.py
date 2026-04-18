

def assert_item_matches_payload(item, payload):
    for field, value in payload.items():
        assert field in item, f"field {field} is missing in {'item'}"
        assert value == item[field], f"field's {'field'} value {value} does not match {'item'}'s value {item[value]}"