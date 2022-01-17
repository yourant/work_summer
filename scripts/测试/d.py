
_list = [
    {
        "origin_id": 1,
        "parent": {
            "id": None
        }
    },
    {
        "origin_id": 3,
        "parent": {
            "id": 2
        }
    },
    {
        "origin_id": 2,
        "parent": {
            "id": 1
        }
    },
    {
        "origin_id": 5,
        "parent": {
            "id": 7
        }
    },
    {
        "origin_id": 6,
        "parent": {
            "id": 1
        }
    },
    {
        "origin_id": 7,
        "parent": {
            "id": 6
        }
    }
    ]

def sort_by_tree(_list, get_id=None, get_parent_id=None, reverse=False):
    """
    列表排序， 适用于数据同步，按照根节点或者叶子优先原则
    """
    if not get_id:
        def get_id(item):
            return item.get('origin_id')
    if not get_parent_id:
        def get_parent_id(item):
            parent = item['parent'] if item.get('parent') else {}
            return parent.get('id')
    id_parent_id_map = {get_id(item): get_parent_id(item) for item in _list}
    item_ids = list(id_parent_id_map.keys())
    item_parent_ids = list(id_parent_id_map.values())
    item_id_index_map = {item_id: index for index, item_id in enumerate(item_ids)}
    target_list = []
    list_len = len(_list)
    while len(target_list) != list_len:
        for index, item_id in enumerate(item_ids[:]):
            if item_parent_ids[index] not in item_ids:
                target_list.append(_list[item_id_index_map[item_id]])
                item_ids.pop(index)
                item_parent_ids.pop(index)
                break
    if reverse:
        return target_list[::-1]
    return target_list


print(sort_by_tree(_list))