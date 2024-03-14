#!/usr/bin/python3
"""
module to return first element in a list
"""
from typing import Sequence, Any, Union


def safe_first_element(lst: Sequence[Any]) -> Union[Any, None]:
    """
    return fisrt list element or none
    """
    if lst:
        return lst[0]
    else:
        return None
