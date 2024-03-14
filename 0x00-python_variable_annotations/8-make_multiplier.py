#!/usr/bin/env python3
"""
module that takes a float as multiplier
and returns function that multiplies float
by multiplier
"""
from typing import Callable


def make_multiplier(multiplier: float) -> Callable[[float], float]:
    """
    takes a float multiplier as argument and returns
    function that maultilies float by multiplier
    """


    def multiplier_func(x: float) -> float:
        """
        performs multiplication
        """
        return x * multiplier

    return multiplier_func
