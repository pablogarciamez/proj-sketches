# proj-sketches

Implementation of the HyperLogLog and Count-Min Sketch algorithms from scratch.

Both algorithms are designed to analyze large datasets while requiring low memory usage.

HyperLogLog estimates the number of distinct elements in a list, while Count-Min Sketch estimates the frequency of a given element within it.

## Installation

```bash
git clone https://github.com/pablogarciamez/proj-sketches.git
cd proj-sketches
pip install -e .
```

## Usage

```python
from proj_sketches import generate_test_data, add_element_to_counters, estimate_cardinality, create_table, add_element, estimate_frequency

data = generate_test_data(1000, 100)

# HyperLogLog

p = 14
counters = [0] * (2**p)
for element in data:
    add_element_to_counters(counters, element, p)
print(estimate_cardinality(counters, p))

# Count-Min Sketch

d, w = 10, 100
table = create_table(d, w)
for element in data:
    add_element(table, element, d, w)
element = "AI"
print(estimate_frequency(table, element, d, w))

```

## Tests

```bash
pip install -e ".[dev]"
pytest
```