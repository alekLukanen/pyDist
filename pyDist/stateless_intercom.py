import urllib3
import json


def get_pool_manager():
    return urllib3.PoolManager()


def post(location, data, headers={"Content-Type": "application/json"}):
    http = get_pool_manager()
    encoded_data = json.dumps(data).encode('utf-8')
    r = http.request('POST', location, body=encoded_data, headers=headers)
    return json.loads(r.data.decode('utf-8'))


def get(location, data):
    http = get_pool_manager()
    r = http.request('GET', location, fields=data)
    print(r.data)
    return json.loads(r.data.decode('utf-8'))


def post_request(ip, port, endpoint, data):
    location = location_assembler(ip, port, endpoint)
    return post(location, data)


def get_request(ip, port, endpoint, data):
    location = location_assembler(ip, port, endpoint)
    return get(location, data)


def location_assembler(ip, port, endpoint):
    address = "http://%s:%d" % (ip, port)
    location = "%s%s" % (address, endpoint)
    return location


def get_counts(ip, port, params={}):
    data = {}
    return get_request(ip, port, "/counts", data)['data']


def post_work_item(ip, port, work_item, params={}):
    work_item_data = work_item.createDictionary()
    work_item_data.update(params)
    return post_request(ip, port, "/addWorkItem", work_item_data)