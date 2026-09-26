import random
import hashlib
import math

def generate_test_data(N, K):
    return [random.randrange(K) for _ in range(N)]

def calculate_cardinality(data_list):
    return len(set(data_list))

def hash_element(element):
    return f"{int(hashlib.sha1(str(element).encode()).hexdigest(), 16):0160b}"

def get_bucket_and_rank(hash_bits, p):
    cube_index = int(hash_bits[:p], 2)
    zero_streak = hash_bits[p:].find("1")
    if zero_streak == -1:
        zero_streak = len(hash_bits) - p
    return (cube_index, zero_streak)

def add_element_to_counters(counters, element, p):
    cube_index, zero_streak = get_bucket_and_rank(hash_element(element), p)
    if counters[cube_index] < zero_streak + 1:
        counters[cube_index] = zero_streak + 1

def estimate_cardinality(counters, p):
    m = 2 ** p
    alpha_m = 0.7213 / (1 + 1.079 / m)
    E = alpha_m * m ** 2 / sum(2 ** (-counters[i]) for i in range(2 ** p))
    if E <= 2.5 * m:
        V = sum(1 for c in counters if c == 0)
        return E if V == 0 else m * math.log(m / V)
    return E