import subprocess
from io import StringIO
import pandas as pd
import sys
import time
from config import WEBHOOK_URL
from config import DISCORD_IDS
import json
import urllib.request

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


def notify_discord(user, finished_jobs):
    mention = f"<@{DISCORD_IDS[user]}>" if user in DISCORD_IDS else ""
    for idx in finished_jobs:
        message = json.dumps({"content": f"{mention} job {idx} is done!"}).encode()
        req = urllib.request.Request(WEBHOOK_URL, data=message, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req)
        print(f"job {idx} is done!")


def main():
    known_jobs = []
    while True:
        known_jobs = active_jobs(user, known_jobs)
        print(f"currently tracking: {known_jobs}")
        time.sleep(300)  # 5 minutes


if __name__ == "__main__":
    main()

"""
ideas:
using discord slash commands, create a command that can change 
the name of specified jobs and a command that can list active jobs.
however, this would require the discord.py library.

get notified when an iteration (e.g. 3d refine, 3d class) is done, although
this would require iterating through file names and not manipulating squeue.
"""