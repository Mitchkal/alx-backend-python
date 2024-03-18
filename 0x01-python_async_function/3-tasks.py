#!/usr/bin/env python3
"""
module that returns an asyncio task
"""

from asyncio import Task
wait_random = __import__('0-basic_async_syntax').wait_random


def task_wait_random(max_delay: int) -> Task:
    """
    returns an asuyncio task
    """
    return Task(wait_random(max_delay))
