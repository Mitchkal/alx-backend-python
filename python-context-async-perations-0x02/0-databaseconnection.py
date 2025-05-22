#!/usr/bin/python3
"""
class based context manager to handle
opening and clossing db connections
automatically
"""


import sqlite3


class DatabaseConnection:
    """
    database connection class
    """
    def __init__(self):
        """
        initialization
        """
        self.connobj = sqlite3.connect('users.db')

    def __enter__(self):
        """
        returns connection object
        """
        return self.connobj

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        closes connection on exit
        """
        self.connobj.close()


with DatabaseConnection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    print(result)
