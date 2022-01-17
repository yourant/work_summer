def set_value(origin_dict, keys, value):
    key = None
    if keys and keys[0]:
        key = keys[0]
    if len(keys) == 1:
        origin_dict[key] = value
    else:
        if origin_dict.__contains__(key) and isinstance(origin_dict.get(key), dict):
            origin_dict[key] = set_value(origin_dict.get(key), keys[1:], value)
        else:
            origin_dict[key] = set_value({}, keys[1:], value)
    return origin_dict

origin_dict = {
    "a": {
        "b": 1
    }
}

origin_dict = set_value(origin_dict, ["a", "b", "c"], 1)
print(origin_dict)
origin_dict = set_value(origin_dict, ['a', "b", "d"], 2)
print(origin_dict)
origin_dict = set_value(origin_dict, ['c', "b", "d"], 2)
print(origin_dict)
origin_dict = set_value(origin_dict, ['d'], 100)
print(origin_dict)