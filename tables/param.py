# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

from __future__ import absolute_import, division


def parse(args):
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


def get():
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

    return sorted(nist.items()) + sorted(petzoldt_98_612.items())


def get_simple():
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

    return petzoldt_98, nist_round2