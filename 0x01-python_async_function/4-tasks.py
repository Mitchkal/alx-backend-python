#!/usr/bin/env python3
"""
module with muliple coroutines
at the same time with async
"""

import asyncio
from typing import List
from asyncio import create_task


task_wait_random = __import__('3-tasks').task_wait_random


async def task_wait_n(n: int, max_delay: int) -> List[float]:
    """
    spawns a coroutine several times and retuens list
    of all delays
    """
    # tasks: List[Task[float]] = [wait_random(max_delay) for _ in range(n)]
    tasks = [task_wait_random(max_delay) for _ in range(n)]
    results = await asyncio.gather(*tasks)
    return sorted(results)
