#!/usr/bin/env python3
import time
import argparse
import json
import umbridge
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed

def model_request(input_data):
    output = model([input_data])[0]
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
print("here")
inputs = [i for i in range(100)]
"""
for i in inputs:
    model(i)
"""
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(model, [[case]]): case for case in inputs}
    i = 0
    for future in as_completed(futures):
        output = future.result()
        print(f"Done {i}")
        i += 1

