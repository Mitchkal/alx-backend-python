#!/usr/bin/env python3
"""
module basic async syntax
contains implementation
of asynchronous routine
"""
import asyncio
from random import uniform


async def wait_random(max_delay: int = 10) -> float:
    """
    takes integer, waits for random delay and
    returns it
    """
    delay = uniform(0, max_delay)
    await asyncio.sleep(delay)
    return delay
