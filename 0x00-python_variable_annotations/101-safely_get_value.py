#!/usr/bin/env python3
"""
module to return a dict value
"""
from typing import Mapping, Any, Union, TypeVar, Optional

T = TypeVar('T')


def safely_get_value(dct: Mapping, key: Any, default:
                     Union[T, None] = None) -> Union[Any, T]:
    """
    safely gets a dictionary value
     """
    if key in dct:
        return dct[key]
    else:
        return default
