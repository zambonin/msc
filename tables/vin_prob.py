#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from math import ceil, sqrt
import param


def prob(q: int, v1: int) -> float:
    return 1 / (q ** v1)


def table_5():
    petzoldt_98, new_nist = param.get_simple()

    t5_line = (
        "{:>3d} & {:>3d} & \\num{{{:6.0E}}} & \\num{{{:6.0E}}} "
        "& \\num{{{:6.0E}}} & \\num{{{:6.0E}}} & \\num{{{:6.0E}}} \\\\\n"
    )
    param_fmt = "$(\\mathbb{{F}}_{{{:>3}}}, {:>2}, {:>2}, {:>2})$"

    contents = ""
    for name, par in sorted(petzoldt_98.items()) + sorted(new_nist.items()):
        q, v1, _, _ = par
        probs = [
            # mean + std of binomial dist with n = v1 and p = 0.5
            prob(q, v1 - ceil(v1 / 2 + sqrt(v1) * 0.5 * std))
            for std in range(5)
        ]
        contents += t5_line.format(q, v1, *probs)

    return contents


if __name__ == "__main__":
    print(table_5())
