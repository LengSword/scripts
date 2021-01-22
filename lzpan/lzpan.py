#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from enum import Enum
from typing import List

import click
import requests
from pydantic.dataclasses import dataclass

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

SEARCH_URL = 'https://s.lzpan.com/search/v1'

PAN_BAIDU_URL = 'https://pan.baidu.com'

HAS_PASS_PREFIX = '/share/init?surl='

NO_PASS_PREFIX = '/s/'


class DiskType(Enum):
    BDY = 'BDY'


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


@dataclass
class OptimizedDiskInfo:
    name: str
    url: str
    password: str


def search_disk_info(name, what='disk', page=1, page_size=20, proxy=''):
    params = {
        'what': what,
        'kw': name,
        'page': page,
        'size': page_size
    }

    proxies = {
        "http": proxy,
        "https": proxy,
    } if proxy else None

    resp = requests.get(SEARCH_URL, params=params, proxies=proxies)

    if resp.status_code != 200:
        click.echo('Error code: {}'.format(resp.status_code))
        return None

    data = resp.json()

    if data['code'] == 200:
        return ResponseInfo(**data)

    return None


def get_disk_url(disk_id, disk_pass):
    if disk_pass:
        return f'{PAN_BAIDU_URL}{HAS_PASS_PREFIX}{disk_id}'
    else:
        return f'{PAN_BAIDU_URL}{NO_PASS_PREFIX}1{disk_id}'


def remove_html_tags(text):
    return re.sub('<.+?>', '', text)


def get_optimized_disk_info(disk_info):
    result = [OptimizedDiskInfo(
        name=remove_html_tags(disk.disk_name),
        url=get_disk_url(disk.disk_id, disk.disk_pass),
        password=disk.disk_pass
    ) for disk in disk_info]

    return result


@click.command(context_settings=CONTEXT_SETTINGS, no_args_is_help=True)
@click.option('--proxy',
              default='',
              help='代理地址(可选)',
              metavar='<proxy-address>')
@click.argument('name', metavar='<搜索文本>')
def search(name, proxy):
    """从懒盘搜索百度网盘分享链接信息
    """
    disk_info = search_disk_info(name=name, proxy=proxy)

    click.echo(f'[+] 模糊查找到 {disk_info.data.total} 条结果')
    click.echo(f'[*] 以下是匹配度最高的前 20 条结果:')

    optimized_disk_info = get_optimized_disk_info(disk_info.data.result)
    click.echo('index - name - url - password')
    for i, disk in enumerate(optimized_disk_info):
        line = f'[{i + 1}] - {disk.name} - {disk.url}'

        if disk.password:
            line += f' - {disk.password}'

        click.echo(line)


if __name__ == '__main__':
    search()
