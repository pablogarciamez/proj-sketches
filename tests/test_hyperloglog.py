import math
import pytest
from proj_sketches import generate_test_data, calculate_cardinality,hash_element, get_bucket_and_rank, add_element_to_counters, estimate_cardinality


def test_hash_element_is_deterministic():
    n = 137
    call1 = hash_element(n)
    call2 = hash_element(n)
    assert call1 == call2

def test_get_bucket_and_rank_no_ones_in_remainder():
    p = 14
    assert get_bucket_and_rank("1" * 14 + "0" * 146, p) == (2 ** 14 - 1, 146)

def test_add_element_keeps_max():
    p_test = 4
    elemento = "cualquier_elemento"

    counters = [0] * (2 ** p_test)
    cube_index, zero_streak = get_bucket_and_rank(hash_element(elemento), p_test)
    valor_real = zero_streak + 1

    # Case 1
    counters[cube_index] = valor_real - 1
    add_element_to_counters(counters, elemento, p_test)
    assert counters[cube_index] == valor_real

    # Case 2
    counters[cube_index] = valor_real + 5
    add_element_to_counters(counters, elemento, p_test)
    assert counters[cube_index] == valor_real + 5

@pytest.mark.parametrize("K", [100, 1000, 5000, 20000, 50000, 200000])
def test_estimate_cardinality_error_within_bound(K):
    p = 14
    N = K * 20
    data = generate_test_data(N, K)
    counters = [0] * (2**p)
    for element in data:
        add_element_to_counters(counters, element, p)
    real = calculate_cardinality(data)
    print(f"Real: {real}")
    estimated = estimate_cardinality(counters, p)
    print(f"Fake: {estimated}")
    error_pct = abs(estimated - real) / real
    assert error_pct < 3 * 1.04 / math.sqrt(2 ** p)