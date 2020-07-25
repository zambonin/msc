#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111,C0330,W0641,R0912,R0913,R0914

from __future__ import absolute_import, division
import param
from math import ceil, sqrt


def public_key_size(
    args,  # instance arguments (q, v_1, o_1, ..., o_u)
    variant="Classic",  # usual, Cyclic (2010), LRS2, Cyclic (NIST)
    convert=True,  # output count in bytes instead of field elements
    homogeneous=True,  # use homogeneous quadratic polynomials only
):
    p = param.parse(args)
    pk = p["m"] * (p["n"] + 1) * (p["n"] + 2) / 2
    blocks = sum(p[f"o{k + 1}"] * p[f"D{k + 1}"] for k in range(p["u"]))

    if variant == "Cyclic":
        pk += p[f"D{p['u']}"] - blocks
    elif variant == "LRS2":
        pk += p["m"] - blocks
    elif variant == "nCyclic":
        pk -= blocks

    if homogeneous:
        pk -= p["m"] * (p["n"] + 1)

    if convert:
        if p["q"] == 16:
            pk /= 2
        elif p["q"] == 31:
            pk = ((pk / 3) * 16 + (pk % 3) * 8) / 8

    return pk


def private_key_size(
    args,  # instance arguments (q, v_1, o_1, ..., o_u)
    eta=0,  # fix at most v_1 terms in the central map
    convert=True,  # output count in bytes instead of field elements
    linear=False,  # drop constant terms in affine maps
    equivalent=False,  # use "equivalent key" lateral maps (implies linear)
    homogeneous=True,  # use homogeneous quadratic polynomials only
):
    p = param.parse(args)
    sk = 0

    if p["u"] <= 2 and equivalent:
        if p["u"] == 2:
            sk += p["o1"] * p["o2"] + p["v1"] * p["o1"] + p["v2"] * p["o2"]
        else:
            sk += p["v1"] * p["o1"]
    else:
        sk += p["n"] ** 2 + p["n"]
        if p["u"] > 1:
            sk += p["m"] ** 2 + p["m"]

        if linear:
            sk -= p["n"] + p["m"]

    for k in range(1, p["u"] + 1):
        v_k, o_k = p[f"v{k}"], p[f"o{k}"]
        sk += o_k * (((v_k - eta) ** 2 + (v_k - eta)) / 2 + (v_k - eta) * o_k)
        if not homogeneous:
            sk += o_k * ((p[f"v{k + 1}"] - eta) + 1)
    sk += eta

    if convert:
        if p["q"] == 16:
            sk /= 2
        elif p["q"] == 31:
            sk = ((sk / 3) * 16 + (sk % 3) * 8) / 8

    return sk


def prk_wrapper(args):
    return (
        private_key_size(args, eta=0, equivalent=True),
        private_key_size(args, eta=args[1], equivalent=True),
    )


def table_1():
    t1_line = (
        "{:<5} & {:<32} & {:>3} & {:>3} & \\num{{{:>8.0f}}} "
        "& \\num{{{:>7.0f}}} & ${:>+6.2f}\\%$ \\\\\n"
    )
    param_fmt = "$(\\mathbb{{F}}_{{{:>3}}}, {:>2}, {:>2}, {:>2})$"

    contents = ""
    for name, par in param.get():
        n, m = sum(par[1:]), sum(par[2:])
        size, new_size = prk_wrapper(par)
        diff = 100 * -(1 - new_size / size)
        contents += t1_line.format(
            name, param_fmt.format(*par), n, m, size, new_size, diff
        )

    return contents


def helper_table_2(params, variants):
    t2_line = "{:<22} & {:<7} & {:>30} & {:>30} & \\num{{{:>8.0f}}} & ${:>+6.2f}\\%$ \\\\\n"
    multi = "\\multirow{{{}}}{{*}}".format(len(variants))

    contents = ""
    for name, par in params.items():
        sk, new_sk = prk_wrapper(par)
        pk = public_key_size(par)

        for var in variants:
            new_pk = public_key_size(par, variant=var)
            diff = 100 * -(1 - (new_sk + new_pk) / (sk + pk))
            sk_m, new_sk_m, name_m = [""] * 3

            if var == "Classic":
                name_m = "{}{{{:<5}}}".format(multi, name)
                sk_m = "{}{{\\num{{{:>7.0f}}}}}".format(multi, sk)
                new_sk_m = "{}{{\\num{{{:>7.0f}}}}}".format(multi, new_sk)

            contents += t2_line.format(
                name_m, var, sk_m, new_sk_m, new_pk, diff,
            )

    return contents


def table_2():
    petzoldt_98, new_nist = param.get_simple()

    contents = ""
    contents += helper_table_2(petzoldt_98, ["Classic", "Cyclic", "LRS2"])
    contents += helper_table_2(new_nist, ["Classic", "nCyclic"])

    return contents


def table_6():
    petzoldt_98, new_nist = param.get_simple()

    t6_line = (
        "{:<32} & ${:>+6.2f}\\%$ & ${:>+6.2f}\\%$ & ${:>+6.2f}\\%$ "
        "& ${:>+6.2f}\\%$ & ${:>+6.2f}\\%$ \\\\\n"
    )
    param_fmt = "$(\\mathbb{{F}}_{{{:>3}}}, {:>2}, {:>2}, {:>2})$"

    contents = ""
    for name, par in sorted(petzoldt_98.items()) + sorted(new_nist.items()):
        old = private_key_size(par, equivalent=True)
        new_sizes = []

        for std in range(5):
            wt = ceil(par[1] / 2 + sqrt(par[1]) * 0.5 * std)
            new = private_key_size(par, eta=wt, equivalent=True)
            new_sizes.append(100 * -(1 - new / old))

        contents += t6_line.format(param_fmt.format(*par), *new_sizes)

    return contents


if __name__ == "__main__":
    # does not consider seed sizes if PRNGs are used
    print(table_1())
    print(table_2())
    print(table_6())
