import hashlib
import math

def get_columns(element, d, w):
    return [int((hashlib.sha1(f"{i}:{element}".encode()).hexdigest()), 16) % w for i in range(d)]

def create_table(d, w):
    return [[0] * w for _ in range(d)]

def add_element(table, element, d, w):
    columns = get_columns(element, d, w)
    for i in range(len(columns)):
        table[i][columns[i]] += 1

def estimate_frequency(table, element, d, w):
    columns = get_columns(element, d, w)
    min = math.inf
    for i in range(len(columns)):
        if table[i][columns[i]] < min:
            min = table[i][columns[i]]
    return min