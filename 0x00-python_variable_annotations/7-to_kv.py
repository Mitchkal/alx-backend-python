#!/usr/bin/env python3
"""
module to create tuple from string and float
"""


def to_kv(k: str, v: [int | float]) -> tuple[str, float]:
    """
    takes input and converts to tuple
    """
    return k, float(v ** 2)
