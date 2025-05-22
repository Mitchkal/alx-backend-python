#!/usr/bin/python3
"""
Reusabele context manager that takes in a query
as input and executes it managing both
connection and query connection
"""

import sqlite3


class ExecuteQuery():
    """
    context manager
    """
    def __init__(self, query, param=None):
        """
        initialization
        """
        self.query = query
        self.param = param or ()
        self.conn = None
        self.cursor = None
        self.result = None

    def __enter__(self):
        """
        entering context manager
        """
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.param)
        self.result = self.cursor.fetchall()
        return self.result

    def __exit__(self, exec_type, exec_val, exec_tb):
        """
        exiting the context manager
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


# Testing The context manager to execute
query = "SELECT * FROM users WHERE age > ?"
params = (25,)

with ExecuteQuery(query, params) as result:
    for row in result:
        print(row)
