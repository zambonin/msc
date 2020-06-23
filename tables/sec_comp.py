#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111,R0914

from __future__ import absolute_import, division
from math import ceil, log2

import param


def security_comp():
    def direct(p, w=2.4):
        return 2 ** (p["m"] * w * (1.38 - 0.63 * w * 1 / log2(p["q"])))

    def collision(p):
        return 2 ** (p["m"] * log2(p["q"]) / 2)

    def uov(p):
        ou = p["o{}".format(p["u"])]
        return p["q"] ** (p["n"] - 1 - 2 * ou) * ou ** 4

    def minrank(p):
        return (
            p["q"] ** (p["v1"] + 1)
            * p["m"]
            * ((p["n"] ** 2 / 2) - (p["m"] ** 2 / 6))
        )

    def highrank(p):
        return p["q"] ** p["o{}".format(p["u"])] * p["n"] ** 3 / 6

    def clamp(a):
        return ceil(log2(a))

    def gates_to_mult(q, a):
        return ceil(log2(2 ** a / (2 * log2(q) ** 2 + log2(q))))

    def wrapper(par):
        p = param.parse(par)
        return (
            clamp(direct(p)),
            clamp(collision(p)),
            clamp(uov(p)),
            clamp(minrank(p)),
            clamp(highrank(p)),
        )

    fmt = "{:6s} & {:33s} & {:>16} & {:>16} & {:>16} & {:>16} & {:>16} \\\\"
    param_fmt = "$(\\mathbb{{F}}_{{{:>3}}}, {:>2}, {:>2}, {:>2})$"

    all_param = param.get()
    former, newer = all_param[:-3], all_param[-3:]

    for name, par in former:
        res = wrapper(par)
        _min = min(res)
        emph = [
            "{:4d}".format(c) if c != _min else "$\\mathbf{{{:4d}}}$".format(c)
            for c in res
        ]
        print(fmt.format(name, param_fmt.format(*par), *emph))

    other_fmt = "{:4s} & {:33s} & {:>16} & {:>16} & {:>16} & {:>16} & {:>16} & {:>16} \\\\"
    levels = param.get_new_sec_levels()
    for name, par in newer:
        lev = levels[name]
        res = list(map(gates_to_mult, [par[0]] * len(lev), lev))
        _min = min(res)
        emph = [
            "{:4d}".format(c) if c != _min else "$\\mathbf{{{:4d}}}$".format(c)
            for c in res
        ]
        print(other_fmt.format(name, param_fmt.format(*par), *emph))


if __name__ == "__main__":
    security_comp()
