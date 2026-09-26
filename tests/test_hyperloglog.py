import math
import pytest
from hyperloglog import (
    generate_test_data, calculate_cardinality,
    hash_element, get_bucket_and_rank, add_element,
    estimate_cardinality,
)

def test_hash_element_is_deterministic():
    n = 137
    call1 = hash_element(n)
    call2 = hash_element(n)
    assert call1 == call2

def test_get_bucket_and_rank_no_ones_in_remainder():
    assert get_bucket_and_rank("1" * 14 + "0" * 146) == (2 ** 14 - 1, 146)

def test_add_element_keeps_max():
    p_test = 4
    element = 137

    counters = [0] * (2 ** p_test)
    cube_index, zero_streak = get_bucket_and_rank(hash_element(element), p_test)
    valor_real = zero_streak + 1

    # Case 1
    counters[cube_index] = valor_real - 1
    add_element(counters, element, p_test)
    assert counters[cube_index] == valor_real

    # Case 2
    counters[cube_index] = valor_real + 5
    add_element(counters, element, p_test)
    assert counters[cube_index] == valor_real + 5

@pytest.mark.parametrize("K", [100, 1000, 5000, 20000, 50000, 200000])
def test_estimate_cardinality_error_within_bound(K):
    p = 14
    cases = [100, 1000, 5000, 20000, 50000, 200000]
    for K in cases:
        N = K * 20
        data = generate_test_data(N, K)
        counters = [0] * (2**p)
        for element in data:
            add_element(counters, element, p)
        real = calculate_cardinality(data)
        estimated = estimate_cardinality(counters, p)
        error_pct = 100 * abs(estimated - real) / real
        assert error_pct < 1.04 / math.sqrt(2**p)