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
        conn = sqlite3.connect("users.db")

        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()

    return wrapper


def transactional(func):
    """
    ensures function running db operation is wrapped inside a
    transaction
    """
    def wrapper(conn, *args, **kwargs):
        """
        wrapper
        """
        try:
            conn.execute('BEGIN')
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result

        except Exception as e:
            conn.rollback()
            print(f"Transaction failed: {e}")
            raise

    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """
    updates users email by id
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email,
                                                               user_id))


# update users email with automatic transaction handling
update_user_email(user_id='ffe15fd6-3fe2-4c7f-beb2-d17f68531aed',
                  new_email='Crawford_Cartwright@hotmail.com')
