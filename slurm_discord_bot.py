import subprocess
from io import StringIO
import pandas as pd
import sys
import time
from config import WEBHOOK_URL
from config import DISCORD_IDS
import json
import urllib.request
import os
import glob
import re

user = "jbpalmer" # edit this for a different user

def active_jobs(user, known_jobs):
    queue = subprocess.run("squeue", capture_output=True, text=True).stdout
    df = pd.read_csv(StringIO(queue), sep=r'\s+', skiprows=0, engine='python')

    my_jobs = df[df['USER'].str.startswith(user)]
    active = my_jobs[~my_jobs['PARTITION'].str.startswith('ood', na=False)]
    current_jobs = list(active["JOBID"])

    finished_jobs = list(set(known_jobs) - set(current_jobs))
    if finished_jobs:
        notify_discord(user, finished_jobs)

    return current_jobs

def get_directory(known_jobs, dirs):
    for idx in known_jobs:
        if idx not in dirs:
            result = subprocess.run(
                ["squeue", "-j", str(idx), "-o", "%o"],
                capture_output=True, text=True
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                dirs[idx] = os.path.dirname(lines[1])
    return dirs

def check_iterations(idx, directory, iterations, user):
    matches = glob.glob(os.path.join(directory, "run_it*_data.star"))

    iter_numbers = [
        int(m.group(1))
        for path in matches
        if (m := re.search(r"_it(\d+)_data\.star", path))
    ]

    if not iter_numbers:
        return

    latest = max(iter_numbers)
    if latest > iterations.get(idx, 0):
        iterations[idx] = latest
        notify_iteration(user, idx, latest)

def notify_iteration(user, idx, iteration):
    mention = f"<@{DISCORD_IDS[user]}>" if user in DISCORD_IDS else ""
    message = json.dumps({"content": f"{mention} job {idx} finished iteration {iteration}"}).encode()
    req = urllib.request.Request(
        WEBHOOK_URL, data=message,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    urllib.request.urlopen(req)

def notify_discord(user, finished_jobs):
    mention = f"<@{DISCORD_IDS[user]}>" if user in DISCORD_IDS else ""
    for idx in finished_jobs:
        message = json.dumps({"content": f"{mention} job {idx} is done!"}).encode()
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=message,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
        )
        urllib.request.urlopen(req)
        print(f"job {idx} is done!")


def main():
    known_jobs = []
    dirs = {}
    iterations = {}

    while True:
        previous_jobs = known_jobs
        known_jobs = active_jobs(user, known_jobs)

        finished = set(previous_jobs) - set(known_jobs)
        for idx in finished:
            dirs.pop(idx, None)
            iterations.pop(idx, None)

        dirs = get_directory(known_jobs, dirs)

        for idx in known_jobs:
            directory = dirs.get(idx)
            if directory and ("Class3D" in directory or "Refine3D" in directory):
                check_iterations(idx, directory, iterations, user)

        print(f"currently tracking: {known_jobs}")
        time.sleep(300) # 5 minutes


if __name__ == "__main__":
    main()
