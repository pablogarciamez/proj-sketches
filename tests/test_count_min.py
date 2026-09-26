from proj_sketches import create_table, add_element, estimate_frequency, generate_test_data
import collections

def test_estimate_frequency():
    d, w = 10, 100
    data = generate_test_data(100000, 1000)
    table = create_table(d, w)
    for element in data: add_element(table, element, d, w)
    real_cardinalities = collections.Counter(data)
    sum_error = 0
    for key in real_cardinalities.keys():
        assert real_cardinalities[key] <= estimate_frequency(table, key, d, w)
        sum_error += estimate_frequency(table, key, d, w) / real_cardinalities[key]
    avg_error = sum_error / len(real_cardinalities.keys())
    assert avg_error < 10
