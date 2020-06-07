#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111,W0641,R0914

from __future__ import absolute_import, division
from math import ceil, log2


def parse_param(args):
    p = {
        "q": args[0],
        "v1": args[1],
        "n": sum(args[1:]),
        "m": sum(args[2:]),
        "u": len(args[2:]),
    }

    for k in range(p["u"]):
        p[f"o{k + 1}"] = args[k + 2]
        vk, ok = p[f"v{k + 1}"], p[f"o{k + 1}"]
        p[f"v{k + 2}"] = vk + ok
        p[f"D{k + 1}"] = vk * ok + (vk ** 2 + vk) / 2

    return p


def public_key_size(
    args,  # instance arguments (q, v_1, o_1, ..., o_u)
    variant="Classic",  # usual, Cyclic (2010), LRS2, Cyclic (NIST)
    convert=True,  # output count in bytes instead of field elements
    homogeneous=True,  # use homogeneous quadratic polynomials only
):
    p = parse_param(args)
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
    eta=False,  # fix v_1 terms in the central map
    convert=True,  # output count in bytes instead of field elements
    linear=False,  # drop constant terms in affine maps
    equivalent=False,  # use "equivalent key" lateral maps (implies linear)
    homogeneous=True,  # use homogeneous quadratic polynomials only
):
    p = parse_param(args)
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

    if eta:
        v_1 = p["v1"]
        for k in range(1, p["u"] + 1):
            v_k, o_k = p[f"v{k}"], p[f"o{k}"]
            sk += o_k * (
                ((v_k - v_1) ** 2 + (v_k - v_1)) / 2 + (v_k - v_1) * o_k
            )
            if not homogeneous:
                sk += o_k * ((p[f"v{k + 1}"] - v_1) + 1)
        sk += v_1
    else:
        for k in range(1, p["u"] + 1):
            v_k, o_k = p[f"v{k}"], p[f"o{k}"]
            sk += o_k * ((v_k ** 2 + v_k) / 2 + v_k * o_k)
            if not homogeneous:
                sk += o_k * (p[f"v{k + 1}"] + 1)

    if convert:
        if p["q"] == 16:
            sk /= 2
        elif p["q"] == 31:
            sk = ((sk / 3) * 16 + (sk % 3) * 8) / 8

    return sk


def prk_wrapper(args):
    return (
        private_key_size(args, eta=False, equivalent=True),
        private_key_size(args, eta=True, equivalent=True),
    )


def table_1():
    nist = {
        "I-a": (16, 32, 32, 32),
        "I-b": (31, 36, 28, 28),
        "I-c": (256, 40, 24, 24),
        "III-b": (31, 64, 32, 48),
        "III-c": (256, 68, 36, 36),
        "IV-a": (16, 56, 48, 48),
        "V-c": (256, 92, 48, 48),
        "VI-a": (16, 76, 64, 64),
        "VI-b": (31, 84, 56, 56),
    }

    petzoldt_98_612 = {
        "P-080": (256, 17, 13, 13),
        "P-100": (256, 26, 16, 17),
        "P-128": (256, 36, 21, 22),
        "P-192": (256, 63, 46, 22),
        "P-256": (256, 85, 63, 30),
    }

    t1_line = (
        "{:<6} & {:<33} & {:>4} & {:>4} & {:>8.0f} & {:>7.0f} "
        "&  ${:>+6.2f}\\%$ \\\\\n"
    )
    param_fmt = "$(\\mathbb{{F}}_{{{:>3}}}, {:>2}, {:>2}, {:>2})$"

    contents = ""
    for name, param in sorted(nist.items()) + sorted(petzoldt_98_612.items()):
        n, m = sum(param[1:]), sum(param[2:])
        size, new_size = prk_wrapper(param)
        diff = 100 * -(1 - new_size / size)
        contents += t1_line.format(
            name, param_fmt.format(*param), n, m, size, new_size, diff
        )

    return contents


def helper_table_2(params, variants):
    t2_line = (
        "{:<23} & {:<8} & {:>25} & {:>25} & {:>8.0f} &  ${:>+6.2f}\\%$ \\\\\n"
    )
    multi = "\\multirow{{{}}}{{*}}".format(len(variants))

    contents = ""
    for name, param in params.items():
        sk, new_sk = prk_wrapper(param)
        pk = public_key_size(param)

        for var in variants:
            new_pk = public_key_size(param, variant=var)
            diff = 100 * -(1 - (new_sk + new_pk) / (sk + pk))
            sk_m, new_sk_m, name_m = [""] * 3

            if var == "Classic":
                name_m = "{}{{{:<5}}}".format(multi, name)
                sk_m = "{}{{{:>7.0f}}}".format(multi, sk)
                new_sk_m = "{}{{{:>7.0f}}}".format(multi, new_sk)

            contents += t2_line.format(
                name_m, var, sk_m, new_sk_m, new_pk, diff,
            )

    return contents


def table_2():
    petzoldt_98 = {
        "P-080": (256, 17, 13, 13),
        "P-100": (256, 26, 16, 17),
        "P-128": (256, 36, 21, 22),
    }

    nist_round2 = {
        "I-a": (16, 32, 32, 32),
        "III-c": (256, 68, 36, 36),
        "V-c": (256, 92, 48, 48),
    }

    contents = ""
    contents += helper_table_2(petzoldt_98, ["Classic", "Cyclic", "LRS2"])
    contents += helper_table_2(nist_round2, ["Classic", "nCyclic"])

    return contents


if __name__ == "__main__":
    # does not consider seed sizes if PRNGs are used
    print(table_1())
    print(table_2())
