import json, requests


def aaa():
    # token = '0cf19accced76e2afa4a1b5ee4fa5cde7a655e32'
    token='hcm00cc10d6e1b0fbe359f43b2569c7da9de9374448'
    param = {"user_id": 1015774, "image_url": 11111, "device_id": 'ASL00011998', "tags": 111, "created_time": 11111,
             "result_num": 1111, "results": 111, "faceliveness": 11111}

    #param = {"depart_id":271746,"begin_date":'2019-01-14',"end_date":'2019-01-14'}
    body={"param":param}
    body = json.dumps(body)
    headers = {"Content-type": "application/x-www-form-urlencoded", "charset": "UTF-8",
               "Accept": "text/plain;application/json",'OuterToken': token}
    #url = 'https://inspur.hcmcloud.cn/api_outer/time.sync.cella.machine.data'
    url = 'http://127.0.0.1:8000/api_outer/time.sync.cella.machine.data'
    req = requests.post(url=url, data=body, headers=headers)
    print(req.json())

aaa()
