#!/usr/bin/python3
from itertools import islice
stream_module = __import__('0-stream_users')

# iterate over the generator function and print only the first 6 rows

for user in islice(stream_module.stream_users(), 6):
    print(user)
