"""Запускаемый модуль"""

from __future__ import annotations
import http.client
from urllib.parse import quote_plus
import json
from pprint import pprint


def main():
    """Главное - тут"""
    im_host = 'im.magnit.ru'
    access_token = 'syt_cGVydnVzaGluX2Rn_jNdUCaZGTkXQRornLrAG_0NnNQT'
    room_id = ''
    base_headers = {
        'Accept': '*/*;q=1.0',
        'User-Agent': 'hkm py robot',
        'Host': im_host,
        }

    conn = http.client.HTTPSConnection(im_host, timeout=10.0)

    print('/.well-known/matrix/client')
    conn.request('GET', '/.well-known/matrix/client', headers=base_headers)
    resp = conn.getresponse()
    assert resp.status == 200
    resp_json = json.load(resp)
    pprint(resp_json)

    print('login types')
    conn.request('GET', '/_matrix/client/v3/login', headers=base_headers)
    resp = conn.getresponse()
    assert resp.status == 200
    resp_json = json.load(resp)
    pprint(resp_json)

    if not access_token:
        print('login with pwd')
        req_body = {
            "device_id": "publishing_robot",
            "initial_device_display_name": "publishing_robot",
            "identifier": {
                "type": "m.id.user",
                "user": f"@pervushin_dg:{im_host}",
                },
            "type": "m.login.password",
            "password": "72mg52ZS#hll",
            }
        conn.request('POST', '/_matrix/client/v3/login', headers=base_headers,
                     body=json.dumps(req_body).encode('utf-8'))
        resp = conn.getresponse()
        assert resp.status == 200
        resp_json = json.load(resp)
        pprint(resp_json)
        access_token = resp_json['access_token']

    print('Server features')
    conn.request(
            'GET', '/_matrix/client/v3/capabilities',
            headers=dict(Authorization=f'Bearer {access_token}', **base_headers))
    resp = conn.getresponse()
    assert resp.status == 200
    resp_json = json.load(resp)
    pprint(resp_json)

    print('Room list')
    conn.request(
            'GET', '/_matrix/client/v3/joined_rooms',
            headers=dict(Authorization=f'Bearer {access_token}', **base_headers))
    resp = conn.getresponse()
    assert resp.status == 200
    resp_json = json.load(resp)
    pprint(resp_json)

    print('Synchronizing')
    filter_str = json.dumps({
        'room': {
            "account_data": {
                "senders": ["@mashkov_ds:im.magnit.ru"]
                }
            }
        })
    conn.request(
            'GET', f'/_matrix/client/v3/sync?filter={quote_plus(filter_str)}',
            headers=dict(Authorization=f'Bearer {access_token}', **base_headers))
    resp = conn.getresponse()
    assert resp.status == 200
    resp_json = json.load(resp)
    pprint(resp_json)

    if not room_id:
        print('Creating room')
        req_body = {
            "creation_content": {
                "m.federate": False,
                },
            "invite": ["@mashkov_ds:im.magnit.ru"],
            "preset": "trusted_private_chat",
            "is_direct": True,
            }
        conn.request(
                'POST', '/_matrix/client/v3/createRoom',
                headers=dict(Authorization=f'Bearer {access_token}', **base_headers),
                body=json.dumps(req_body).encode('utf-8'))
        resp = conn.getresponse()
        assert resp.status == 200
        resp_json = json.load(resp)
        pprint(resp_json)
        room_id = resp_json['room_id']

    print('Message sending')
    req_body = {
        "body": "hello from robot 3",
        "msgtype": "m.text",
        }
    conn.request(
            #'PUT', '/_matrix/client/v3/rooms/!nUGynzCsRSEBkALozF:im.magnit.ru/send/m.room.message/1',
            'PUT', f'/_matrix/client/v3/rooms/{room_id}/send/m.room.message/4',
            headers=dict(Authorization=f'Bearer {access_token}', **base_headers),
            body=json.dumps(req_body).encode('utf-8'))
    resp = conn.getresponse()
    assert resp.status == 200
    resp_json = json.load(resp)
    pprint(resp_json)


from random import randint, seed
from urllib.parse import urlparse, urlunparse
from itertools import product, chain, zip_longest
from math import sqrt, floor, factorial, gcd
from collections import Counter
from functools import wraps
from typing import NamedTuple, List
from contextlib import suppress
from abc import abstractmethod, ABC
from bisect import insort
import re
from copy import copy

def open(i, j):
    rv = result.split('\n')[i].split()[j]
    return str(int(rv))

gamemap, result = '  '


#from preloaded import open

def area_gen(c_row, c_col, row_count, col_count):
    for i_row in range(max(0, c_row - 1), min(row_count, c_row + 2)):
        for i_col in range(max(0, c_col - 1), min(col_count, c_col + 2)):
            yield i_row, i_col

def solve_mine(map, n):
    # coding and coding...
    def cell_solve(c_col, c_row) -> bool:
        nonlocal n
        c_val = map[c_row][c_col]
        if c_val in '?x':
            return False
        c_val = int(c_val)
        mine_count = 0
        cell_count = 0
        close_count = 0
        for i_row, i_col in area_gen(c_row, c_col, row_count, col_count):
            cell_count += 1
            mine_count += map[i_row][i_col] == 'x'
            close_count += map[i_row][i_col] == '?'
        if c_val == (mine_count + close_count) and 0 < close_count:
            for i_row, i_col in area_gen(c_row, c_col, row_count, col_count):
                if map[i_row][i_col] == '?':
                    map[i_row][i_col] = 'x'
                    n -= 1
            return True
        if c_val == mine_count and 0 < close_count:
            for i_row, i_col in area_gen(c_row, c_col, row_count, col_count):
                if map[i_row][i_col] == '?':
                    map[i_row][i_col] = open(i_row, i_col)
            return True
        return False

    map = [[x for x in row.split()] for row in map.split('\n')]
    n -= map.count('x')
    row_count = len(map)
    col_count = len(map[0])
    is_changed = True
    while 0 < n and is_changed:
        is_changed = False
        for i_row in range(row_count):
            for i_col in range(col_count):
                old_cell = map[i_row][i_col]
                if old_cell in '?x':
                    continue
                is_changed = cell_solve(i_col, i_row) or is_changed
    return '\n'.join([' '.join(x for x in row) for row in map])

if __name__ == '__main__':
    seed(1)
    gamemap = """
? ? ? ? ? ?
? ? ? ? ? ?
? ? ? 0 ? ?
? ? ? ? ? ?
? ? ? ? ? ?
0 0 0 ? ? ?
""".strip()
    result = """
1 x 1 1 x 1
2 2 2 1 2 2
2 x 2 0 1 x
2 x 2 1 2 2
1 1 1 1 x 1
0 0 0 1 1 1
""".strip()
    print(solve_mine(gamemap, result.count('x')))
