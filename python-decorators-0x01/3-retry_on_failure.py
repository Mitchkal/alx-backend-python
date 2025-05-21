#!/usr/bin/python3
"""
decorator to open database connection
pass it to a function and close it.
"""

import sqlite3
import functools
import time


def with_db_connection(func):
    """
    decorator function
    """

    def wrapper(*args, **kwargs):
        """
        wrapper to pass connection to
        func, and close when it is done
        """
        conn = sqlite3.connect("users.db")

        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()

    return wrapper


def retry_on_failure(retries=3, delay=2):
    """
    decorator factory to retry on failure
    """
    def decorator(func):
        """
        decorator
        """
        def wrapper(*args, **kwargs):
            """
            wrapper function to
            retry function calls
            """
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < retries - 1:
                        time.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """
    updates users email by id
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


# attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users)
