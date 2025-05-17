#!/usr/bin/python3
"""
use of generator to compute a memory efficient
aggreagtion function; average for large dataset
"""
seed = __import__('seed')


def stream_user_ages():
    """
    generator to stream user ages from user_data
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")
    for row in cursor:
        yield float(row['age'])
    connection.close()


def compute_average():
    """
    computes and prints average of ages
    """
    total_age = 0
    count = 0

    for age in stream_user_ages():
        total_age += age
        count += 1

    if count > 0:
        print(f"Average age of users: {total_age / count:.2f}")
    else:
        print("No users found.")


if __name__ == "__main__":
    compute_average()
