#!/usr/bin/python3
""""
Lazy pagination with a generator
"""
seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    fetches next pag when needed at an offset of 0
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT \
                   {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_paginate(page_size):
    """
    implements the paginate_users
    function
    """
    offset = 0

    while True:
        rows = paginate_users(page_size, offset)
        if not rows:
            break
        yield rows
        offset += page_size
