#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "httpx",
#     "tqdm",
# ]
# ///

import asyncio
import sys
from typing import Any, Awaitable, Callable, Coroutine

import httpx
from tqdm.asyncio import tqdm


def get_semaphore_wrapper(
    semaphore: asyncio.Semaphore | None = None,
) -> Callable[[Awaitable], Coroutine]:
    async def wrapper(awaitable):
        if not semaphore:
            return await awaitable

        async with semaphore:
            return await awaitable

    return wrapper


async def get_hook_manifest(
    client: httpx.AsyncClient, mirror: str
) -> list[dict[str, Any]]:
    response = await client.get(mirror + "/update-data/metadata/hook_v3.json")
    response.raise_for_status()
    return response.json()


async def get_dict_manifest(
    client: httpx.AsyncClient, mirror: str
) -> list[dict[str, Any]]:
    response = await client.get(mirror + "/update-data/metadata/dict_v3.json")
    response.raise_for_status()
    return response.json()


async def probe_url(client: httpx.AsyncClient, url: str) -> None:
    response = await client.get(url)
    response.raise_for_status()
    # print(".", end="", flush=True)


async def main():
    if len(sys.argv) < 2:
        mirror = "https://dfint.github.io"
    else:
        mirror = "https://" + sys.argv[1]

    print("Checking mirror", mirror)
    print("Loading manifests...")

    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            hook_task = tg.create_task(get_hook_manifest(client, mirror))
            dict_task = tg.create_task(get_dict_manifest(client, mirror))

    print("Done.")

    hook_data = hook_task.result()
    dict_data = dict_task.result()

    print("Checking URLs...")
    semaphore = asyncio.Semaphore(20)
    wrapper = get_semaphore_wrapper(semaphore)
    async with httpx.AsyncClient() as client:
        tasks = []
        for item in hook_data:
            tasks.extend(
                [
                    asyncio.create_task(
                        wrapper(probe_url(client, mirror + item["lib"]))
                    ),
                    asyncio.create_task(
                        wrapper(probe_url(client, mirror + item["config"]))
                    ),
                    asyncio.create_task(
                        wrapper(probe_url(client, mirror + item["offsets"]))
                    ),
                    asyncio.create_task(
                        wrapper(probe_url(client, mirror + item["dfhooks"]))
                    ),
                ]
            )

        for item in dict_data:
            tasks.extend(
                [
                    asyncio.create_task(
                        wrapper(probe_url(client, mirror + item["csv"]))
                    ),
                    asyncio.create_task(
                        wrapper(probe_url(client, mirror + item["font"]))
                    ),
                    asyncio.create_task(
                        wrapper(probe_url(client, mirror + item["encoding"]))
                    ),
                ]
            )

        for task in tqdm.as_completed(tasks):
            await task

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
