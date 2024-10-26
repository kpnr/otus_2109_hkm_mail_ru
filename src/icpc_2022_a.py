"""challenge from Misha"""
from typing import List, Tuple, Set, Dict, Union
from time import time


def f_table_make(n: int) -> List[int]:
    """make factiorial table from 1 to n"""
    rv, f = [0], 1
    for x in range(1, n + 1):
        f *= x
        rv.append(f)
    return rv


def f_table_normalize(fti: List[int]) -> List[str]:
    """Normalize f-table by len (0-pad from left)"""
    s = str(fti[-1])
    rv, norm = [], len(s)
    for x in fti:
        s = str(x)
        # s = '0' * (norm - len(s)) + s
        rv.append(s)
    return rv


def fs(n: int, p: int) -> str:
    s = fts[n]
    p -= len(fts[-1]) - len(s)
    if 0 <= p:
        return s[p]
    return '0'


def ft_split(n_set: Set[int], bad_set: Set[int]) -> Tuple[int, dict]:
    """split fts by best digit"""

    def next_pos():
        i = max((i for i in n_set))
        s = fts[i]
        for p, c in enumerate(reversed(s)):
            if c != '0':
                break
        d = len(fts[-1]) - p - 1
        # while 0 <= p:
        #     yield p
        #     p -= 1
        # lens.sort()
        # d = len(fts[-1]) - lens[len(lens) // 2]
        u = d + 1
        go = True
        while go:
            go = False
            if 0 <= d:
                yield d
                d -= 1
                go = True
            if u < len(fts[-1]):
                yield u
                u += 1
                go = True

    def get_best_pos() -> int:
        """get best position for classification"""
        fts_len = len(n_set)
        best_pos, best_set = -1, set()
        for pos in next_pos():
            if pos in bad_set:
                continue
            return pos
            digit_set = set()
            for i in n_set:
                digit_set.add(fs(i, pos))
                if min(7, fts_len) <= len(digit_set):
                    return pos  # good enough
            if len(best_set) < len(digit_set):
                best_pos, best_set = pos, digit_set
        return best_pos

    def classify() -> Dict[str, List[str]]:
        """classify fts by buckets"""
        rv = {}
        for i in n_set:
            rv.setdefault(fs(i, best_pos), set()).add(i)
        return rv

    best_pos = get_best_pos()
    best_dict = classify()
    for k in best_dict.keys():
        v = best_dict[k]
        if 1 < len(v):
            best_dict[k] = ft_split(v, bad_set | {best_pos})
    return best_pos, best_dict


def guess_x(buckets) -> int:
    """make a guess"""
    while True:
        best_pos, best_dict = buckets
        d = input(f"Digit at postion {len(fts[-1]) - best_pos}:")
        guess = best_dict[d]
        if isinstance(guess, set):
            return next(iter(guess))
        buckets = guess

class PropTest:
    prop: int = 0


if __name__ == '__main__':
    a = PropTest()
    b = PropTest()
    PropTest.prop = 99
    a.prop = 1
    # b.prop = 2
    print(f'Class={PropTest.prop} a={a.prop} b={b.prop}')
    t = time()
    n = 1000
    # n = 5982
    fti = f_table_make(n)
    fts = f_table_normalize(fti)
    f_buckets = ft_split(set(range(len(fts))), set())
    print(f"Prepared in {time() - t}")
    print("\nI guess:", guess_x(f_buckets))
    # x = timeit('f_table_make(5982)', number=1, globals=globals())
    # print(x)
