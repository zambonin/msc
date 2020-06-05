#!/usr/bin/env sage
# -*- coding: utf-8 -*-

from sys import argv
from typing import Tuple


def part_fixed_rand_transf(
    q: int, n: int, v: int, it: int, fix: bool = False
) -> Tuple[RealField]:
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

    Rf = RealField(1 << 6)
    if not fix:
        return (
            Rf(std(results)),
            Rf(sqrt((q ** 2 - 1) / 12)),
            Rf(mean(results)),
            Rf((q - 1) / 2),
        )

    return Rf(std(results)), Rf(mean(results))


@parallel
def part_fixed_wrapper(
    q: int, n: int, v: int, it: int
) -> Tuple[Tuple[RealField]]:
    return (
        part_fixed_rand_transf(q, n, v, it, 0),
        part_fixed_rand_transf(q, n, v, it, 1),
    )


if __name__ == "__main__":
    q, t, nv = map(int, argv[1:])
    assert q >= 2 and t >= 1 and nv in (42, 90)

    param = (25 + 17, 17) if nv == 42 else (55 + 35, 35)
    poss = [
        (g, *param, it)
        for g in prime_powers(2, q + 1)
        for it in range(1, t + 1)
    ]

    for x, y in part_fixed_wrapper(poss):
        q, n, v, it = x[0]
        std_no, std_exp, mean_no, mean_exp = y[0]
        std_yes, mean_yes = y[1]
        print(
            q, it, n, v,
            std_no, std_yes, std_exp, abs(std_no - std_yes),
            mean_no, mean_yes, mean_exp, abs(mean_no - mean_yes),
        )
