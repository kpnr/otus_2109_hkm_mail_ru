"""Запускаемый модуль"""

from __future__ import annotations
import http.client
import time
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
from itertools import product, chain, zip_longest, permutations
from math import sqrt, floor, factorial, gcd
from collections import Counter
from functools import wraps
from typing import NamedTuple, List
from contextlib import suppress
from abc import abstractmethod, ABC
from bisect import insort
import re
from copy import copy

from itertools import product, permutations
from contextlib import suppress
def equal_to_24(a,b,c,d):
    ops_f = (
        lambda x, y: x + y,
        lambda x, y: x - y,
        lambda x, y: x * y,
        lambda x, y: x / y,
    )
    ops_s = {id(op): op_s for op, op_s in zip(ops_f, '+-*/')}
    for args in permutations((a, b, c, d), 4):
        # print(args)
        for ops in product(ops_f, repeat=3):
            result = 0
            with suppress(ZeroDivisionError):
                # ((a ? b) ? c) ? d
                result = ops[2](ops[1](ops[0](args[0], args[1]), args[2]), args[3])
            if result == 24:
                rv = '(((' + str(args[0])
                for arg, op in zip(args[1:], ops):
                    rv += ops_s[id(op)] + str(arg) + ')'
                return rv
            with suppress(ZeroDivisionError):
                # (a ? b) ? (c ? d)
                result = ops[2](ops[0](args[0], args[1]), ops[1](args[2], args[3]))
            if result == 24:
                rv = '(' + str(args[0]) + ops_s[id(ops[0])] + str(args[1]) + ')'
                rv += ops_s[id(ops[2])] + '(' + str(args[2]) + ops_s[id(ops[1])] + str(args[3]) + ')'
                return rv
            with suppress(ZeroDivisionError):
                # a ? (b ? (c ? d))
                result = ops[2](args[0], ops[1](args[1], ops[0](args[2], args[3])))
            if result == 24:
                rv = str(args[0]) + ops_s[id(ops[2])] + '(' + str(args[1]) + ops_s[id(ops[1])]
                rv += '(' + str(args[2]) + ops_s[id(ops[0])] + str(args[3]) + '))'
                return rv
            with suppress(ZeroDivisionError):
                # a ? ((b ? c) ? d)
                result = ops[2](args[0], ops[1](ops[0](args[1], args[2]), args[3]))
            if result == 24:
                rv = str(args[0]) + ops_s[id(ops[2])] + '((' + str(args[1]) + ops_s[id(ops[0])]
                rv += str(args[2]) + ')' + ops_s[id(ops[1])] + str(args[3]) + ')'
                return rv

    return "It's not possible!"


if __name__ == '__main__':
    start = time.perf_counter()
    print(equal_to_24(32, 84, 92, 22))
    print(f'time={time.perf_counter()-start}')
