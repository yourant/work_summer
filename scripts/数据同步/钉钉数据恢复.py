import json
import xlrd
import requests
import time

get_sub_depart_url = 'https://oapi.dingtalk.com/topapi/v2/department/listsub?access_token=6c81837290d537448aa400a5d193a3ef'

update_depart_url = "https://oapi.dingtalk.com/topapi/v2/department/update?access_token=6c81837290d537448aa400a5d193a3ef"

# access_token = "6c81837290d537448aa400a5d193a3ef"

def force_request(method, **kwargs):
    while True:
        try:
            kwargs.update(timeout=(2, 10))
            response = eval(f'requests.{method}')(**kwargs)
            if response.json().get('errcode') != 0:
                print(response.json())
            elif response.json().get('errcode') == 15:
                continue
            return response.json()
        except Exception as err:
            print(err)
            time.sleep(2)
            pass

def find_parent_outer_id(parent_id, data_list):
    for item in data_list:
        if parent_id == item.get('origin_id'):
            if not item.get('outer_id') and not item.get('my_outer_id'):
                raise Exception(f'parent_id: {parent_id} 未找到 父级 outer_id')
            if item.get('outer_id'):
                return item.get('outer_id'), 1
            return item.get('my_outer_id'), 2

# json_dict = {}

# def new_sort_by_tree(_list, get_id=None, get_parent_id=None, reverse=False):
#     """
#     列表排序， 适用于数据同步，按照根节点或者叶子优先原则
#     """
#     if not get_id:
#         def get_id(item):
#             return item.get('origin_id')
#     if not get_parent_id:
#         def get_parent_id(item):
#             return item.get('parent_id')
#     id_parent_id_map = {get_id(item): get_parent_id(item) for item in _list}
#     item_ids = list(id_parent_id_map.keys())
#     item_id_index_map = {item_id: index for index, item_id in enumerate(item_ids)}
#     target_list = []
#     list_len = len(_list)


#     while len(target_list) != list_len:
#         print(len(target_list))
#         for index, item_id in enumerate(item_ids[:]):
#             if id_parent_id_map[item_id] not in item_ids:
#                 target_list.append(_list[item_id_index_map[item_id]])
#                 item_ids.pop(index)
#                 break
#     if reverse:
#         return target_list[::-1]
#     return target_list

# wb = xlrd.open_workbook('./scripts/department_history.xls')
# sheet = wb.sheet_by_name('Sheet1')

# data_list = []
# for a in range(2, sheet.nrows):
#     data_dict = {
#         "outer_id": None,
#         "order": None,
#         "name": None,
#         "origin_id": None,
#         "parent_id": None 
#     }
#     cells = sheet.row_values(a)
    
#     # 字段处理
#     data_dict['outer_id'] = int(cells[22]) if cells[22] else None
#     data_dict['parent_id'] = int(cells[19]) if cells[19] else None
#     data_dict['origin_id'] = int(cells[21]) if cells[21] else None
#     data_dict['name'] = cells[4]
#     data_dict['order'] = cells[8]
#     data_list.append(data_dict)

# data_list = new_sort_by_tree(data_list)
json_dict = {}

with open('./d.json', errors='ignore', encoding='utf-8') as fp:
    json_dict = json.load(fp)
data_list = json_dict['data']


i= 0
for item in data_list:
    if item.get('name') == '中建二局三公司':
        continue
    if not item.get('outer_id'):
        outer_parent_id, _type = find_parent_outer_id(item.get('parent_id'), data_list)
        response = force_request("post", url=get_sub_depart_url, json={"dept_id": outer_parent_id})
        if response.get('errcode') != 0:
            print(f'return error, {response}, {send_data}')
            break
        else:
            sub_dept_list = response.get('result') 
            # if set([item.get('name') for item in sub_dept_list])
            same_name_items = [item1 for item1 in sub_dept_list if item1.get('name') == item.get('name')]
            if len(same_name_items) > 1:
                print(f"same_name_items: {same_name_items}, item: {item}")
                break
            if not same_name_items:
                continue
            item['my_outer_id'] = same_name_items[0].get('dept_id')
            with open('./e.json', 'a', encoding='utf-8') as write_file:
                write_file.write(str(item))
        # 检查根组织路径
        pass
    else:
        # 执行更新
        outer_parent_id, _type = find_parent_outer_id(item.get('parent_id'), data_list)
        # 如果是自带则跳过
        if _type == 1:
            continue
        i += 1
        print(i)
        send_data = {
                "name": item.get('name'), 
                "parent_id": outer_parent_id, 
                "dept_id": item.get('outer_id')
                
            }
        if item.get('order'):
            send_data['order'] = item.get("order")
        response = force_request('post', url=update_depart_url, json=send_data
            
        )        
        if response.get('errcode') != 0:
            print(f'return error, {response}, {send_data}')
            break
    



