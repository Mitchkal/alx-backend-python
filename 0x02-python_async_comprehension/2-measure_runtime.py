#!/usr/bin/emv python3
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
    await async_comprehension()
    return (time.time() - start)
