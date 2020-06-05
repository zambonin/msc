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


def valid_param(args):
    p = parse_param(args)
    alpha = 1.5
    l = 128

    return all(
        (
            all(i > 0 for i in p.values()),
            p["m"] >= alpha * p[f"o{p['u']}"],
            p["n"] >= p["m"],
            p["m"] >= 10,
            p["v1"] >= l / log2(p["q"]) - 1,
            p[f"o{p['u']}"] >= l / log2(p["q"]),
            p["n"] - 2 * p[f"o{p['u']}"] >= l / log2(p["q"]) + 1,
            p["n"] >= ceil(5 / 3 * (p["m"] - 1)),
        )
    )


def public_key_size(args, variant="classic", convert=False):
    def cyclic():
        tmp1 = p[f"D{p['u']}"] + p["m"] * ((p["n"] + 1) * (p["n"] + 2)) / 2
        tmp2 = sum(p[f"o{k + 1}"] * p[f"D{k + 1}"] for k in range(p["u"]))
        return tmp1 - tmp2

    def lrs2():
        tmp1 = p["m"] * ((p["n"] + 1) * (p["n"] + 2) + 2) / 2
        tmp2 = sum(p[f"o{k + 1}"] * p[f"D{k + 1}"] for k in range(p["u"]))
        return tmp1 - tmp2

    def classic():
        return p["m"] * (p["n"] + 1) * (p["n"] + 2) / 2

    p = parse_param(args)
    pk = locals()[variant.lower()]()

    if convert:
        if p["q"] == 16:
            pk /= 2
        elif p["q"] == 31:
            pk = ((pk / 3) * 16 + (pk % 3) * 8) / 8

    return pk


def private_key_size(args, eta=False, convert=False):
    p = parse_param(args)

    sk = p["n"] ** 2 + p["n"]
    if p["u"] > 1:
        sk += p["m"] ** 2 + p["m"]

    if eta:
        v_1 = p["v1"]
        for k in range(1, p["u"] + 1):
            v_k, o_k = p[f"v{k}"], p[f"o{k}"]
            sk += o_k * (
                ((v_k - v_1) ** 2 + (v_k - v_1)) / 2
                + (v_k - v_1) * o_k
                + (p[f"v{k + 1}"] - v_1)
                + 1
            )
        sk += v_1
    else:
        for k in range(1, p["u"] + 1):
            v_k, o_k = p[f"v{k}"], p[f"o{k}"]
            sk += o_k * ((v_k ** 2 + v_k) / 2 + v_k * o_k + p[f"v{k + 1}"] + 1)

    if convert:
        if p["q"] == 16:
            sk /= 2
        elif p["q"] == 31:
            sk = ((sk / 3) * 16 + (sk % 3) * 8) / 8

    return sk


def prk_wrapper(args):
    return (
        private_key_size(args, eta=False, convert=True),
        private_key_size(args, eta=True, convert=True),
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

    petzoldt_612 = {
        "P-080": (256, 17, 17, 9),
        "P-100": (256, 26, 22, 21),
        "P-128": (256, 36, 28, 15),
        "P-192": (256, 63, 46, 22),
        "P-256": (256, 85, 63, 30),
    }

    t1_line = "{:<6} & {:<33} & {:>4} & {:>4} & {:>8.0f} & {:>7.0f} & ${:>+6.2f}\\%$ \\\\"
    param_fmt = "$(\\mathbb{{F}}_{{{:>3}}}, {:>2}, {:>2}, {:>2})$"

    for name, param in sorted(nist.items()) + sorted(petzoldt_612.items()):
        old_prk, eta_prk = prk_wrapper(param)
        n, m = sum(param[1:]), sum(param[2:])
        diff = 100 * -(1 - eta_prk / old_prk)
        print(
            t1_line.format(
                name, param_fmt.format(*param), n, m, old_prk, eta_prk, diff
            )
        )


def table_2():
    petzoldt_98 = {
        "P-080": (256, 17, 13, 13),
        "P-100": (256, 26, 16, 17),
        "P-128": (256, 36, 21, 22),
    }

    variants = ["Classic", "Cyclic", "LRS2"]
    t2_line = "{:<23} & {:<50} & {:>8} & {:>24} & {:>23} & {:>7.0f} & ${:>+6.2f}\\%$ \\\\"
    param_fmt = "$(\\mathbb{{F}}_{{{:>3}}}, {:>2}, {:>2}, {:>2})$"
    multirow = "\\multirow{{{}}}{{*}}".format(len(variants))

    for name, param in sorted(petzoldt_98.items()):
        old_prk, eta_prk = prk_wrapper(param)
        old_puk = public_key_size(param)
        for var in variants:
            new_puk = public_key_size(param, variant=var)
            pair_diff = 100 * -(1 - (eta_prk + new_puk) / (old_prk + old_puk))
            old_prk_multi, eta_prk_multi, param_multi, name_multi = [""] * 4
            if var == "Classic":
                name_multi = "{}{{{:<5}}}".format(multirow, name)
                param_multi = "{}{{{:<32}}}".format(
                    multirow, param_fmt.format(*param)
                )
                old_prk_multi = "{}{{{:>6.0f}}}".format(multirow, old_prk)
                eta_prk_multi = "{}{{{:>5.0f}}}".format(multirow, eta_prk)
            print(
                t2_line.format(
                    name_multi,
                    param_multi,
                    var,
                    old_prk_multi,
                    eta_prk_multi,
                    new_puk,
                    pair_diff,
                )
            )


if __name__ == "__main__":
    table_1()
    print()
    table_2()
