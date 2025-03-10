import umbridge
import subprocess
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

print("Client start.")

# Get port
try:
    port = os.getenv("PORT")
except:
    port = 4242
if (port == None):
    port = 4242
print("Client is using port:", port)

# Get host
if len(sys.argv) > 1:
    host = sys.argv[1]
else:
    # Define the bash command you want to run
    bash_command = "hostname"

    # Run the bash command using subprocess
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    # Print the output of the bash command
    # print(output.decode())
    host = output.decode()[:-1]
url = "http://"+host+":"+str(port)
print("Connecting to server at:", url)
model = umbridge.HTTPModel(url, "forward")

# Parallel evaluation
print("Starting parallel evaluation request.")
params = [[i] for i in range(10)]
with ThreadPoolExecutor(max_workers=2) as executor:
    futures = {executor.submit(model, [params[i]]): i for i in range(10)}
    for future in as_completed(futures):
        print(f"Input: {params[futures[future]]}")
        print(f"Output: {future.result()}")
