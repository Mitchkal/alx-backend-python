#!/usr/bin/python3
"""
Logs database queries by executed function
"""


import sqlite3
import functools
from datetime import datetime

# decorator to lof sql queries


def log_queries(func):
    """
    decorator that logs sql queries
    """
    def wrapper(*args, **kwargs):
        """
        function wrapper
        """
        query = kwargs.get("query") if "query" in kwargs \
            else (args[0] if args else "<no query>")
        print(f"{datetime.now()}: Query: {query}")
        result = func(*args, **kwargs)
        return result
    return wrapper


@log_queries
def fetch_all_users(query):
    """
    query to fetch all users from db
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# fetch users while logging queries


users = fetch_all_users(query="SELECT * FROM users")
