#!/usr/bin/python3
"""
asynchronous sqlite3
implementation
"""
import aiosqlite
import asyncio


async def async_fetch_users():
    """asynchronous user fetching
    """
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return rows
            # print("\n All users:")
            # for row in rows:
                # print(row)


async def async_fetch_older_users():
    """
    asynchronous user fecthing with filter
    """
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            rows = await cursor.fetchall()
            return rows
            # print("\n Users older than 40:")
            # for row in rows:
                # print(row)


async def fetch_concurrently():
    """
    function to fetch queries asynchronously
    """
    await asyncio.gather(
            async_fetch_users(),
            async_fetch_older_users()
    )


if __name__ == "__main__":
    """
    main
    """
    asyncio.run(fetch_concurrently())
