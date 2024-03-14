#!/usr/bin/env python3
"""
module to create tuple from string and float
"""
from typing import Union, Tuple


def to_kv(k: str, v: Union[int, float]) -> Tuple[str, float]:
    """
    takes input and converts to tuple
    """
    return k, float(v ** 2)
