import json
import os 
from dateutil import parser
import pickle

def extract_times(run_dir, run_name, iterations=None):
    data = {}
    with open(f"{run_dir}/{run_name}.txt", "r") as f:
        for line in f:
            if line[0] == "{":
                json_line = json.loads(line)
                event = json_line["event"]
                if "job" in event:
                    time = parser.parse(json_line["time"])
                    job_num = event["job"]
                    event_type = event["type"]
                    if event_type == "job-created":
                        data[str(job_num)] = {} # Check validity 
                        data[str(job_num)].update({"created": time})
                    elif event_type == "task-started":
                        data[str(job_num)].update({"started": time})
                    elif event_type == "task-canceled":
                        data[str(job_num)].update({"canceled": time})
                    elif event_type == "job-completed":
                        data[str(job_num)].update({"ended": time})
                    else:
                        raise Exception("NULL event detected")
                else:
                    continue
    if iterations is not None:
        for i in reversed(range(iterations)):
            keys = list(data.keys())[::-1]
            data[str(i)] = data.pop(keys[i])

    for i in data:
        submit = data[i]["created"].timestamp()
        start = data[i]["started"].timestamp()
        canceled = data[i]["canceled"].timestamp()
        end = data[i]["ended"].timestamp()
        makespan = end - submit
        cpu_time = canceled - start 
        data[i].update({"makespan": makespan, "lag": makespan - canceled + start, "cpu-time": cpu_time, "slr": makespan / cpu_time})
        

    with open(f"{run_dir}/{run_name}-hq.pkl", "wb") as file:
        pickle.dump(data, file)


run_dir = "10jobs"
run_name = "gp"
extract_times(run_dir, run_name)

"""
roughly 3ms overhead between job creation and task initiation
"""


