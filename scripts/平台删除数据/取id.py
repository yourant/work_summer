import json

json_dict = {}
with open("./scripts/平台删除数据/id_dicts.json", errors='ignore') as fp:
    json_dict = json.load(fp)

# hcm.model.remove.batch 移除接口
id_dicts = json_dict["result"]["result"]

id_list = [item['id'] for item in id_dicts]

print('id_list', len(id_list), '去重后：', len(set(id_list)))
with open('./scripts/平台删除数据/id_list.txt', 'w') as fp1:
    fp1.write(str(id_list))