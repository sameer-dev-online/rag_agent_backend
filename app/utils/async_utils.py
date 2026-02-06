"""
Async utilities.
"""

import asyncio
from typing import Any, Callable, List, TypeVar

T = TypeVar("T")


async def run_async_tasks(tasks: List[Callable[..., Any]]) -> List[Any]:
    """
    Run multiple async tasks concurrently.

    Args:
        tasks (List[Callable]): List of async callables.

    Returns:
        List[Any]: Results from each task.
    """
    results = await asyncio.gather(*[task() for task in tasks], return_exceptions=True)
    return results
