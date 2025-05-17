#!/usr/bin/python3
"""
Generator to stream rows
from sql database one by one
"""


import mysql.connector
from mysql.connector import errorcode
import csv
import uuid


DB_NAME = "ALX_prodev"

TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_data (
user_id CHAR(36) PRIMARY KEY,
name VARCHAR(255) NOT NULL,
email VARCHAR(255) NOT NULL,
age INT NOT NULL,
INDEX (user_id)
)
"""


def connect_db():
    """
    Connects to MYQL server
    """
    try:
        connection = mysql.connector.connect(
            user='root',
            host="localhost",
            password='12121963'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Connection error: {err}")
        return None


def create_database(connection):
    """
    Creates the ALX_prodev database
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")


def connect_to_prodev():
    """
    connects to the ALX_prodev database
    """
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="12121963",
            database=DB_NAME
        )
    except mysql.connection.Error as err:
        print(f"Connection to ALX_prodev failed: {err}")
        return None


def create_table(connection):
    """ creates the user data table if not exists"""
    try:
        cursor = connection.cursor()
        cursor.execute(TABLE_SCHEMA)
        cursor.close()
        print(f"Table user_data created succesfully")
    except mysql.connector.Error as err:
        print(f"Table creation failed: {err}")


def insert_data(connection, data):
    """ Inserts data from csv file to user_data
    """
    try:
        with open(data, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            data = [(str(uuid.uuid4()), row["name"],
                    row["email"], row["age"]) for row in reader]

        cursor = connection.cursor()
        query = """
        INSERT IGNORE INTO user_data (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(query, data)
        connection.commit()
        cursor.close()
        # print(f"{len(data)} records processed.")
    except Exception as e:
        print(f"Error inserting data: {e}")


def stream_users(connection):
    """
    Generator that Yields one row at a time from user data
    """
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")
    for row in cursor:
        yield row
    cursor.close()
