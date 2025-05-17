#!/usr/bin/python3
"""
generator to fetch and process
data in batches from users database
"""
import mysql.connector
from mysql.connector import errorcode

DB_NAME = "ALX_prodev"

config = {
        "user": "root",
        "host": "localhost",
        "password": "12121963",
        "database": DB_NAME
        }


def stream_users_in_batches(batch_size):
    """
    fetches rows in batches from users_table
    """
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        print("Error connecting to Database", err)
        return

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        batch = []
        for row in cursor:
            batch.append(row)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print("Error executing query", err)
        if connection.is_connected():
            connection.close()


def batch_processing(batch_size):
    """
    processes each batch to filter users over age 25
    """
    for batch in stream_users_in_batches(batch_size):
        filtered = [user for user in batch if float(user['age']) > 25]
        yield filtered
