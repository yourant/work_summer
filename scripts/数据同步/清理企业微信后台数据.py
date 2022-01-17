import os
import requests
import time


# corp_id = 'ww851d2e61b4ca3fbe'

# corp_secret = 'HzQ6dVyKXYjtr6cU-VEY0dXtQtIEwjhnB5rfYSDK-pU'

# 葛洲坝测试
# corp_id = 'ww5aad87732dd41d2d'

# corp_secret = 'EaLlHojGYOEr7JoZPLgqOoDI5RmiWVxuAr9vtxZSUoQ'

# 葛洲坝正式
corp_id = 'ww382be08e50cea90c'

corp_secret = 'S4SSigZMrzm6NdEd7R9vkVYXmr3zafV_QDIgapq9DK4'


get_access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'

get_user_list_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/simplelist'

# 
get_depart_url = 'https://qyapi.weixin.qq.com/cgi-bin/department/list'

# 更新人员
update_user_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/update'

# 批量删除人员
bulk_del_user_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/batchdelete'

# 删除人员

del_user_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/delete'

# 删除部门
del_depart_url = 'https://qyapi.weixin.qq.com/cgi-bin/department/delete'

def write_log_result(source_type, file_path):
    """
    记录删除记录装饰器
    """
    def wrapper(fn):
        def inner(*args, **kwargs):
            response = fn(*args, **kwargs)
            result_msg = f'{source_type},{args[1:]},{kwargs}'
            success_or_failure = ' success'
            if response.get('errcode') != 0:
                success_or_failure = f'response: {response} failure'
            result_msg += success_or_failure + '\n'
            with open(file_path, mode='a') as fp:
                fp.write(result_msg)
            return response
        return inner
    return wrapper

def force_request(method, **kwargs):
    while True:
        try:
            kwargs.update(timeout=(2, 10))
            response = eval(f'requests.{method}')(**kwargs)
            return response.json()
        except Exception as err:
            time.sleep(2)
            pass


class CleanQYWorkAddressBook:


    USER = 'User'
    DEPART = 'Depart'
    RESULT_FILE_PATH = './delete_QYwork.log'

    def __init__(self) -> None:
        self.access_token = self.get_access_token(corp_id, corp_secret)
        if os.path.exists(self.RESULT_FILE_PATH):
            os.remove(self.RESULT_FILE_PATH)
    
    def get_access_token(self, corp_id, corp_secret):
        result = force_request('get', url=get_access_token_url, params={"corpid": corp_id, "corpsecret": corp_secret})
        return result.get('access_token')

    def get_user_list(self, **kwargs):
        """
        通过部门获取人员id
        """
        params = {
            "access_token": self.access_token
        }
        params.update(kwargs)
        result = force_request('get', url=get_user_list_url, params=params)
        return result.get('userlist')

    @write_log_result(USER, RESULT_FILE_PATH)
    def bulk_delete_user(self, user_id_list):
        """
        批量删除人员 一次最多200个
        """
        url = f'{bulk_del_user_url}?access_token={self.access_token}'
        response = force_request('post', url=url, json={"useridlist": user_id_list})
        return response


    @write_log_result(USER, RESULT_FILE_PATH)
    def delete_user(self, user_id):
        """
        人员一个个删除
        """
        params = {
            "access_token": self.access_token
        }
        params['userid'] = user_id
        response = force_request('get', url=del_user_url, params=params)
        return response

    def get_depart_list(self, **kwargs):
        params = {
            'access_token': self.access_token
        }
        params.update(kwargs)
        response = force_request('get', url=get_depart_url, params=params)
        response = response
        department_list = response.get('department')
        return department_list

    @write_log_result(DEPART, RESULT_FILE_PATH)
    def delete_depart(self, depart_id):
        params = {
            "access_token": self.access_token,
        }
        params['id'] = depart_id
        response = force_request('get', url=del_depart_url, params=params)
        return response
    
    def bulk_delete_depart(self, depart_id_list):
        """
        批量删除
        """
        for depart_id in depart_id_list:
            self.delete_depart(depart_id=depart_id)
    
    # 汇总的删除方法
    def delete(self, source_type, id_list):
        if source_type == self.USER:
            group_user_id = self.group_by_id_list(id_list)
            for group_item in group_user_id:
                response = self.bulk_delete_user(group_item)
                if response.get('errcode') == 0:
                    continue
                for user_id in group_item:
                    response = self.delete_user(user_id)
                    # 表示是企业微信创建人，不允许删除
                    if response.get('errcode') == 301005:
                        self.move_user_to_depart(user_id, 1)
        elif source_type == self.DEPART:
            self.bulk_delete_depart(id_list)
    
    def move_user_to_depart(self, user_id, depart_id):
        url = f"{update_user_url}?access_token={self.access_token}"
        response = force_request('post', url=url, json={'department': [depart_id], 'userid': user_id})
        return response
    
    def group_by_id_list(self, id_list, group_len=199):
        """
        id， 分组
        """
        user_group_list = []
        start = 0
        user_list_len = len(id_list)
        while start < user_list_len:
            user_group_list.append(id_list[start:start + group_len])
            start = start + group_len
        return user_group_list

    def run(self):
        root_id = 1
        # user_list = self.get_user_list(department_id=root_id, fetch_child=1)
        # user_id_list = [item.get('userid') for item in user_list]
        # self.delete(self.USER, user_id_list)
        depart_list = self.get_depart_list(id=root_id)
        depart_list = new_sort_by_tree(depart_list, get_id=lambda item : item.get("id"), get_parent_id=lambda item: item.get('parentid'), reverse=True)
        # depart_list = depart_list[::-1]
        depart_id_list = [item.get("id") for item in depart_list]
        self.delete(self.DEPART, depart_id_list)


def new_sort_by_tree(_list, get_id=None, get_parent_id=None, reverse=False):
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
    item_id_index_map = {item_id: index for index, item_id in enumerate(item_ids)}
    target_list = []
    list_len = len(_list)
    while len(target_list) != list_len:
        for index, item_id in enumerate(item_ids[:]):
            if id_parent_id_map[item_id] not in item_ids:
                target_list.append(_list[item_id_index_map[item_id]])
                item_ids.pop(index)
                break
    if reverse:
        return target_list[::-1]
    return target_list


if __name__ == '__main__':
    qywork = CleanQYWorkAddressBook()
    """
    遇到的错误码
    301005,
    60005
    60006
    """
    qywork.run()
