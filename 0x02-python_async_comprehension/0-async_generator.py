#!/usr/bin/env python3
"""
module async generator
contains a coroutine async generator
"""
from random import uniform
import asyncio
from typing import Generator


async def async_generator() -> Generator[float, None, None]:
    """
    loops 110 times and in each
    async waits 1 second, then yields
    random number btn 0 and 10
    """
    for _ in range(10):
        await asyncio.sleep(1)
        yield uniform(0, 10)
