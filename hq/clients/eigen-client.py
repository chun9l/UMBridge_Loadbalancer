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

parser = argparse.ArgumentParser(description='Model output test.')
parser.add_argument('url', metavar='url', type=str,
                    help='the URL on which the model is running, for example http://localhost:4242')
args = parser.parse_args()

print(f"Connecting to host URL {args.url}")
model = umbridge.HTTPModel(args.url, "posterior")
dimension = 100
job_count =50
inputs = [dimension for i in range(100)]
"""
for i in inputs:
    model(i)
"""
with ThreadPoolExecutor(max_workers=job_count) as executor:
    futures = {executor.submit(model, [[case]]): case for case in inputs}
    i = 0
    for future in as_completed(futures):
        output = future.result()
        print(f"Done {i}")
        i += 1

