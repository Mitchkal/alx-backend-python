#!/usr/bin/env python3
"""
module with func to sum a mixed list
"""
from typing import List, Union


def sum_mixed_list(mxd_lst: List[Union[int | float]]) -> float:
    """
    find sum of mixed list and return float
    """
    return float(sum(mxd_lst))
