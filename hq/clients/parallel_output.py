#!/usr/bin/env python3
import time
import argparse
import json
import umbridge
import pytest
from concurrent.futures import ThreadPoolExecutor

def model_request(input_data):
    output = model([input_data])[0]
    #print(output)
    return output

def check_output(output, expected, message):
    assert pytest.approx(output[0]) == expected, message

def load_test_cases(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    additional_test_cases = []
    for item in data:
        input_vec = (item['input_x'], item['input_y'])
        output = item['output']
        message = f"Output not as expected for input {input_vec}"
        additional_test_cases.append((list(input_vec), output, message))
    return additional_test_cases

parser = argparse.ArgumentParser(description='Model output test.')
parser.add_argument('url', metavar='url', type=str,
                    help='the URL on which the model is running, for example http://localhost:4242')
args = parser.parse_args()

print(f"Connecting to host URL {args.url}")
model = umbridge.HTTPModel(args.url, "posterior")

# Original list of inputs and expected outputs
test_cases = [
    ([0.0, 0.0], -204.84848484848487, "Output not as expected for input [0.0, 0.0]"),
    ([2.0, 2.0], -1.581180343024592, "Output not as expected for input [2.0, 2.0]")
]

# Load additional test cases from JSON file
additional_cases = load_test_cases('model_output_results.json')
test_cases.extend(additional_cases)

#for test_case in test_cases:
#    output = model_request(test_case[0])
#    check_output(output, test_case[1], test_case[2])
# Using ThreadPoolExecutor to parallelize model calls
start = time.perf_counter()

with ThreadPoolExecutor() as executor:
    futures = {executor.submit(model_request, case[0]): case for case in test_cases}

    for future in futures:
        case = futures[future]
        output = future.result()
        check_output(output, case[1], case[2])

time_spent = time.perf_counter() - start

print(f"done in {time_spent:.2f}s")

