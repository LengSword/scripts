#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from enum import Enum
from pydantic.dataclasses import dataclass
from typing import List

import requests

# proxies = {
#     "http": 'http://localhost:7890',
#     "https": 'http://localhost:7890',
# }

SEARCH_URL = 'https://s.lzpan.com/search/v1'

PAN_BAIDU_URL = 'https://pan.baidu.com'

HAS_PASS_PREFIX = '/share/init?surl='

NO_PASS_PREFIX = '/s/'


class DiskType(Enum):
    BDY = "BDY"


@dataclass
class DiskInfo:
    disk_id: str
    disk_type: DiskType
    disk_pass: str
    disk_user: str
    disk_name: str
    disk_info: str
    alias: str


@dataclass
class ResponseData:
    result: List[DiskInfo]
    took: int
    total: int


@dataclass
class ResponseInfo:
    code: int
    data: ResponseData
    msg: str


def search(name, what='disk', page=1, page_size=20):
    params = {
        'what': what,
        'kw': name,
        'page': page,
        'size': page_size
    }
    # resp = requests.get(SEARCH_URL, params=params, proxies=proxies)
    resp = requests.get(SEARCH_URL, params=params)

    if resp.status_code != 200:
        print('Error code: {}'.format(resp.status_code))
        return None

    data = resp.json()

    if data['code'] == 200:
        return ResponseInfo(**data)

    return None


def get_disk_url_info(disk_data):
    if disk_data.disk_pass:
        return (f'{PAN_BAIDU_URL}{HAS_PASS_PREFIX}{disk_data.disk_id}'
                f'@{disk_data.disk_pass}')
    else:
        return f'{PAN_BAIDU_URL}{NO_PASS_PREFIX}1{disk_data.disk_id}'


def remove_html_tags(text):
    return re.sub('<.+?>', '', text)


def get_all_disk_data(disk_info):
    for i, disk in enumerate(disk_info):
        name = remove_html_tags(disk.disk_name)
        url = get_disk_url_info(disk)
        print(f'[{i + 1}] - {name} - {url}')


if __name__ == '__main__':
    disk_info = search(name='小肩膀')
    print(f'[+] 模糊查找到 {disk_info.data.total} 条结果')
    print(f'以下是匹配度最高的前 20 条结果:')
    get_all_disk_data(disk_info.data.result)
