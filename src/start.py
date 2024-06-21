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
    return int(rv)

gamemap, result = '  '


#from preloaded import open
from dataclasses import dataclass

@dataclass
class CellStats:
    mine_goal: int
    mine_open: int
    closed: set
    empty: int

@dataclass
class SolveResult:
    empty_cells: set
    mine_cells: set
    eqs: list


def cell_stat_get(map: list[list[str]], c_row: int, c_col:int) -> CellStats:
    row_count = len(map)
    col_count = len(map[0])
    rv = CellStats(mine_goal=int(map[c_row][c_col]), mine_open=0, closed=set(), empty=0)
    for c_val, row, col in ((map[r][c], r, c) for r, c in area_gen(c_row, c_col, row_count, col_count)):
        if c_val == '?':
            rv.closed.add((row, col))
        elif c_val == 'x':
            rv.mine_open += 1
        else:
            rv.empty += 1
    rv.closed = frozenset(rv.closed)
    return rv


def area_gen(c_row, c_col, row_count, col_count):
    for i_row in range(max(0, c_row - 1), min(row_count, c_row + 2)):
        for i_col in range(max(0, c_col - 1), min(col_count, c_col + 2)):
            yield i_row, i_col

def area_gen2(c_row, c_col, row_count, col_count):
    for i_row in range(max(0, c_row - 2), min(row_count, c_row + 3)):
        for i_col in range(max(0, c_col - 2), min(col_count, c_col + 3)):
            yield i_row, i_col

def make_eqs(map, vars: set, numbers: set, mines_closed: int) -> list:
    eq_dict = {frozenset(vars): mines_closed}
    for eq_row, eq_col in numbers:
        eq_stat = cell_stat_get(map, eq_row, eq_col)
        if not eq_stat.closed:
            continue
        eq_dict[frozenset(eq_stat.closed)] = eq_stat.mine_goal - eq_stat.mine_open
    rv = [(set(eq[0]), eq[1]) for eq in eq_dict.items()]
    return rv


def single_solve(eq_var: set, eq_val: int, vars_zero: set, vars_mine: set):
    eq_var = eq_var - vars_zero
    eq_mines = eq_var & vars_mine
    if eq_mines:
        eq_var -= eq_mines
        eq_val -= len(eq_mines)
    if eq_val == 0:
        vars_zero.update(eq_var)
        eq_var = set()
    elif len(eq_var) == eq_val:
        vars_mine.update(eq_var)
        eq_var = set()
        eq_val = 0
    return (eq_var, eq_val)


def matrix_solve(eqs: list) -> SolveResult:
    vars_zero = set()
    vars_mine = set()
    eqs = eqs[:]
    eq3_var, eq3_val = set(), 0
    is_done = not eqs
    while not is_done:
        is_done = True
        for eq1_i, (eq1_var, eq1_val) in enumerate(eqs):
            eq_solved = single_solve(eq1_var, eq1_val, vars_zero, vars_mine)
            if eq_solved != (eq1_var, eq1_val):
                eqs[eq1_i] = (eq1_var, eq1_val) = eq_solved
                is_done = False
            if not eq1_var:
                continue
            for eq2_i in range(eq1_i+1, len(eqs)):
                (eq2_var, eq2_val) = eqs[eq2_i]
                eq_solved = single_solve(eq2_var, eq2_val, vars_zero, vars_mine)
                if eq_solved != (eq2_var, eq2_val):
                    eqs[eq2_i] = (eq2_var, eq2_val) = eq_solved
                    is_done = False
                if not eq2_var:
                    continue
                eq3_i = -1
                eq1_and_2_var = eq1_var & eq2_var
                eq1_len = len(eq1_var)
                eq2_len = len(eq2_var)
                eq1_and_2_len = len(eq1_and_2_var)
                if not eq1_and_2_len:
                    pass
                elif eq1_len == eq1_and_2_len and eq2_len == eq1_and_2_len:
                    eq3_var, eq3_val, eq3_i = set(), 0, eq2_i
                elif eq1_var == eq1_and_2_var:
                    eq3_var = eq2_var - eq1_and_2_var
                    eq3_val = eq2_val - eq1_val
                    eq3_i = eq2_i
                elif eq2_var == eq1_and_2_var:
                    eq3_var = eq1_var - eq1_and_2_var
                    eq3_val = eq1_val - eq2_val
                    eq3_i = eq1_i
                    (eq1_var, eq1_val) = (eq3_var, eq3_val)
                elif eq1_len - eq1_and_2_len == eq1_val - eq2_val:
                    eq3_var = eq1_var - eq1_and_2_var
                    eq3_val = eq1_val - eq2_val
                    eq3_i = eq1_i
                    (eq1_var, eq1_val) = (eq3_var, eq3_val)
                elif eq2_len - eq1_and_2_len == eq2_val - eq1_val:
                    eq3_var = eq2_var - eq1_and_2_var
                    eq3_val = eq2_val - eq1_val
                    eq3_i = eq2_i
                if 0 <= eq3_i:
                    eqs[eq3_i] = (eq3_var, eq3_val)
                    is_done = False
        eqs = [x for x in eqs if x[0]]
        is_done = is_done or not eqs
    return SolveResult(empty_cells=vars_zero, mine_cells=vars_mine, eqs=eqs)


def guess_solve(eqs: list) -> SolveResult:
    var_set = {var for e in eqs for var in e[0]}
    for guess_var in var_set:
        solution_0 = matrix_solve(eqs + [({guess_var}, 0)])
        solution_1 = matrix_solve(eqs + [({guess_var}, 1)])
        always_empty = solution_0.empty_cells & solution_1.empty_cells
        always_mine = solution_0.mine_cells & solution_1.mine_cells
        if always_empty or always_mine:
            return SolveResult(empty_cells=always_empty, mine_cells=always_mine, eqs=eqs)
    return SolveResult(empty_cells=set(), mine_cells=set(), eqs=eqs)


def solve_mine(map_str, mines_closed):
    map = [[x for x in row.split()] for row in map_str.split('\n')]
    row_count = len(map)
    col_count = len(map[0])
    cells_unknown = set()
    cells_to_solve = set()
    for row in range(row_count):
        for col in range(col_count):
            cell_value = map[row][col]
            if cell_value == 'x':
                mines_closed -= 1
                continue
            if cell_value == '?':
                cells_unknown.add((row, col))
                continue
            cell_stat = cell_stat_get(map, row, col)
            if not cell_stat.closed:
                continue
            cells_to_solve.add((row, col))
    while cells_unknown:
        eqs = make_eqs(map, cells_unknown, cells_to_solve, mines_closed)
        cells_solved = matrix_solve(eqs)
        eqs = cells_solved.eqs
        cells_mine_and_empty = cells_solved.empty_cells | cells_solved.mine_cells
        if not cells_mine_and_empty:
            cells_solved = guess_solve(eqs)
            cells_mine_and_empty = cells_solved.empty_cells | cells_solved.mine_cells
        if not cells_mine_and_empty:
            break
        for r, c in cells_solved.empty_cells:
            try:
                map[r][c] = str(open(r, c))
            except:
                print('\n'.join([' '.join(x for x in row) for row in map]))
                raise
        for r, c in cells_solved.mine_cells:
            map[r][c] = 'x'
        mines_closed -= len(cells_solved.mine_cells)
        cells_unknown -= cells_mine_and_empty
        cells_to_solve = set()
        for r, c in cells_solved.empty_cells | cells_solved.mine_cells:
            for ra, ca in area_gen2(r, c, row_count, col_count):
                if map[ra][ca] in '?x' or (ra, ca) in cells_to_solve:
                    continue
                if any(map[rb][cb] == '?' for rb, cb in area_gen(ra, ca, row_count, col_count)):
                    cells_to_solve.add((ra, ca))
    rv = '\n'.join([' '.join(x for x in row) for row in map])
    if cells_unknown:
        print(rv)
        return '?'
    return rv

if __name__ == '__main__':
    seed(1)
    import copy
    gamemap = """
1 1 1 1 1
x 2 3 x 2
2 ? ? x 2
? ? 3 3 2
? ? ? 2 x
? ? ? 2 1
""".strip()
    result = """
1 1 1 1 1
x 2 3 x 2
2 x 3 x 2
2 3 3 3 2
x 2 x 2 x
1 2 1 2 1
""".strip()
    start = time.perf_counter()
    print(solve_mine(copy.deepcopy(gamemap), result.count('x')))
    # for i in range(10):
    #     solve_mine(copy.deepcopy(gamemap), result.count('x'))
    print(f'time={time.perf_counter()-start}')
