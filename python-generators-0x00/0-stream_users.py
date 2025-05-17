#!/usr/bin/python3
"""
generator to stream rows from
SQL database one by one
"""
import mysql.connector
from mysql.connector import errorcode


DB_NAME = "ALX_prodev"


def stream_users():
    """
    uses generator to fetch rows
    from user_data table
    """

    config = {
            "host": "127.0.0.1",
            "user": "root",
            "password": "12121963",
            "database": DB_NAME
            }
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        print("Error connecting to DB:", err)
        return
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        for row in cursor:
            yield row

        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print("Error executing query:", err)
        if connection.is_connected():
            connection.close()
