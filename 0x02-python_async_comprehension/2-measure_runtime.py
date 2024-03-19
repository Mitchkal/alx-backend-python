#!/usr/bin/env python3
"""
module measure runtime
"""
import time
import asyncio

async_comprehension = __import__('1-async_comprehension').async_comprehension


async def measure_runtime() -> float:
    """
    returns total runtime of
    an async comprehension
    routine
    """
    start = time.time()
    tasks = [async_comprehension() for _ in range(4)]
    await asyncio.gather(*tasks)
    return (time.time() - start)
