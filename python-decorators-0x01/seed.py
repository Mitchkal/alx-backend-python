#!/usr/bin/python3
"""
seeds user table in sqlite3db
"""


import sqlite3
import csv
import uuid
import sys


TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
id CHAR(36) PRIMARY KEY,
name VARCHAR(255) NOT NULL,
email VARCHAR(255) NOT NULL,
age INT NOT NULL
)
"""


def connect_and_seed(data):
    """connects to sqlite database and seeds
    it
    """
    con = sqlite3.connect("users.db")
    if con:
        print("Connection succesful")
    else:
        print("connection failed")

    cursor = con.cursor()

    # create database
    try:
        cursor.execute(TABLE_SCHEMA)
    except Exception as err:
        print("Error creating table", err)
        return

    try:
        with open(data, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            user_rows = [(str(uuid.uuid4()), row["name"],
                    row["email"], int(row["age"])) for row in reader]

            query = """
                    INSERT OR IGNORE INTO users (id, name, email, age)
                    VALUES(?, ?, ?, ?)
            """
            cursor.executemany(query, user_rows)
            con.commit()
    except Exception as e:
        print(f"Error inserting data:{e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: script_name.py <arg1>")
    else:
        arg1 = sys.argv[1]
        connect_and_seed(arg1)
