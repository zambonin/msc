#!/usr/bin/env sage
# -*- coding: utf-8 -*-

from functools import reduce
from itertools import product
from operator import mul
from sys import argv
from typing import List, Tuple


def naive_prod(q: int, n: int) -> Rational:
    return reduce(mul, (1 - q ^ (-i) for i in range(1, n + 1)), 1)


@cached_function
def euler_id(q: int, n: int) -> Rational:
    # increasing `n` does not make much of a difference
    return sum(((-1) ^ k) * q ^ (-k * (3 * k - 1) / 2) for k in range(-n, n))


@cached_function
def split(a: int, n: int) -> List[int]:
    k, m = divmod(a, n)
    return [(i + 1) * k + min(i + 1, m) for i in range(n)]


def compose_naive(q: int, n: int, u: int = 2) -> Rational:
    return reduce(mul, (naive_prod(q, i) for i in split(n, u)), 1)


def compose_euler(q: int, n: int, u: int = 2) -> Rational:
    return reduce(mul, (euler_id(q, i) for i in split(n, u)), 1)


@parallel
def process(q: int, n: int, u: int = 2) -> Tuple[RealField]:
    Rf = RealField(1 << 7)  # convert to decimal with high precision
    return (
        Rf(naive_prod(q, n)),
        Rf(euler_id(q, n)),
        Rf(compose_naive(q, n, u)),
        Rf(compose_euler(q, n, u)),
    )


if __name__ == "__main__":
    q, l1, l2 = map(int, argv[1:])
    assert q >= 2 and l2 >= l1 >= 2

    param = list(product(prime_powers(2, q + 1), range(l1, l2 + 1)))
    for x, y in process(param):
        print("{:4d} {:4d} {} {} {} {}".format(*x[0], *y))
