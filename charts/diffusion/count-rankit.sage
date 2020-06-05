#!/usr/bin/env sage
# -*- coding: utf-8 -*-

from collections import Counter
from operator import itemgetter
from sys import argv
from typing import Iterable, Tuple

from numpy import random


def part_fixed_rand_transf(
    q: int, n: int, v: int, it: int, fix: bool = False
) -> Iterable[Tuple[int, int, float]]:
    k = GF(q)
    assert n > v and k.is_field()

    set_random_seed()

    transf = random_matrix(k, n)
    while not transf.is_invertible():
        transf = random_matrix(k, n)

    fixed = random_vector(k, v)
    cast = int if q.is_prime() else lambda x: x.integer_representation()

    results = []
    for _ in range(it):
        variable = random_vector(k, n)
        if fix:
            variable[n - v :] = fixed
        results += map(cast, transf * variable)

    return zip(
        sorted(Counter(results).items(), key=itemgetter(1)),
        sorted(random.normal(size=q)),
    )


if __name__ == "__main__":
    t, fix = int(argv[1]), bool(argv[2] == "fix")
    assert t > 0

    q, n, v = 256, 55 + 35, 35
    for k, v in part_fixed_rand_transf(q, n, v, t, fix):
        print(k[0], k[1], v)
