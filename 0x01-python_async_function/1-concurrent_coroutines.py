#!/usr/bin/env python3
"""
module with muliple coroutines
at the same time with async
"""

import asyncio
from typing import List
from asyncio import Task


wait_random = __import__('0-basic_async_syntax').wait_random


async def wait_n(n: int, max_delay: int) -> list[float]:
    """
    spawns an async coroutine several times and retuens list
    of all delays
    """
    tasks: List[Task[float]] = [wait_random(max_delay) for _ in range(n)]
    results = await asyncio.gather(*tasks)
    return sorted(results)
