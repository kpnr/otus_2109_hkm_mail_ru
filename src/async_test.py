"""async testing"""
import asyncio
import inspect
async def af(a,b):
    await asyncio.sleep(1)
    return a+b

def swait(f):
    async def it():
        yield f

    if not inspect.isawaitable(f):
        return f
    r = [await w async for w in it()]
    r = list(r)
    try:
        f = f.send(None)
    except StopIteration as e:
        return e.value
    raise RuntimeError('not sync and not coroutine result')


def sf(a,b):
    r = swait(af(a, b))
    return r

async def main():
    x = await af(1, 2)
    print(x)
    x = sf(1, 2)
    print(x)

if __name__ == '__main__':
    asyncio.run(main())