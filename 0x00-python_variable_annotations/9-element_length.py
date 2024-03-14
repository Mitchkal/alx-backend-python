#!/usr/bin/env python3
"""
function to return iterable
"""
from typing import Iterable, List, Sequence, Tuple


def element_length(lst: Iterable[Sequence]) -> List[Tuple[Sequence, int]]:
    """
    returns an iterable
    """
    return [(i, len(i)) for i in lst]
