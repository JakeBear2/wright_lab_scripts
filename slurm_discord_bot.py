import subprocess
from io import StringIO
import pandas as pd
import sys
import time

user = "jbpalmer" # edit this for a different user

def active_jobs(user, known_jobs):
    queue = subprocess.run("squeue", capture_output=True, text=True).stdout
    df = pd.read_csv(StringIO(queue), sep=r'\s+', skiprows=0, engine='python')

    my_jobs = df[df['USER'].str.startswith(user)]
    active = my_jobs[~my_jobs['PARTITION'].str.startswith('ood', na=False)]
    current_jobs = list(active["JOBID"])

    finished_jobs = list(set(known_jobs) - set(current_jobs))
    if finished_jobs:
        notify_discord(finished_jobs)

    return current_jobs


def notify_discord(finished_jobs):
    # discord webhook call goes here eventually
    for idx in finished_jobs:
        print(f"job {idx} is done!")


def main():
    known_jobs = []
    while True:
        known_jobs = active_jobs(user, known_jobs)
        print(f"currently tracking: {known_jobs}")
        time.sleep(300)  # 5 minutes


if __name__ == "__main__":
    main()