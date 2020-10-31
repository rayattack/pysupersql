import asyncio
from functools import wraps, partial


def asynchronize(func):
    @wraps
    async def delegate(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        partial_function = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, partial_function)
    return delegate


def synchronize(func):
    @wraps
    def delegate(*args, **kwargs):
        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            return asyncio.get_event_loop().run_until_complete(result)
        return result
    return delegate
