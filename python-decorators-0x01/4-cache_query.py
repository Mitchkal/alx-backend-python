#!/usr/bin/python3
"""
Decorator to cache results of db
queries to avoid redundant calls
"""


import time
import sqlite3
import functools


query_cache = {}


def cache_query(func):
    """
    decorator to cache
    query responses
    """

    def wrapper(*args, **kwargs):
        """wrapper"""
        query = kwargs.get("query")
        if query not in query_cache:
            print("fetching from db")
            result = func(*args, **kwargs)
            query_cache.update({query: result})
            return result
        else:
            print("fetched from cache")
            return query_cache.get(query)

    return wrapper


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


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# first call will cache results
users = fetch_users_with_cache(query="SELECT * FROM users")
print(users)

# Second call will use cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(users)
