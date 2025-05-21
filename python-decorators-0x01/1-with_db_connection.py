#!/usr/bin/python3
"""
decorator to open database connection
pass it to a function and close it.
"""

import sqlite3
import functools


def with_db_connection(func):
    """
    decorator function
    """

    def wrapper(*args, **kwargs):
        """
        wrapper to pass connection to
        func, and close when it is done
        """
        connection = sqlite3.connect("users.db")
        user_id = str(args[0] if args else kwargs.get("user_id"))

        try:
            result = func(connection, user_id)
            return result
        finally:
            connection.close()

    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    """
    gets users from db by user_id
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id, ))
    return cursor.fetchone()


# Fetch user by ID with automatic connection handling
user = get_user_by_id(user_id=1)
# user = get_user_by_id(user_id="ffe15fd6-3fe2-4c7f-beb2-d17f68531aed")
print(user)
