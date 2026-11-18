import subprocess
from io import StringIO
import pandas as pd
import sys
import time

user = "jbpalmer" # edit this for a different user

def active_jobs(user, queue):
    df = pd.read_csv(StringIO(queue), sep=r'\s+', skiprows=0, engine='python')
    my_jobs = df[df['USER'].str.startswith(user)]
    active_jobs = my_jobs[~my_jobs['PARTITION'].str.startswith('ood', na=False)]
    job_ids = active_jobs["JOBID"]

    return job_ids

def check_jobs(id_list, queue):
    still_running = []
    for idx in id_list:
        if str(idx) not in queue:
            print(f"job {idx} is done!")
        else:
            print(f"job {idx} is currently running.")
            still_running.append(idx)
            
    return still_running

def main():
    queue = subprocess.run("squeue", capture_output=True, text=True).stdout
    id_list = []

    if user in queue:
        job_ids = active_jobs(user, queue)
    else:
        print("cannot be found")
        sys.exit(0)

    for idx in job_ids:
        id_list.append(idx)
    
    while len(id_list) > 0:
        queue = subprocess.run("squeue", capture_output=True, text=True).stdout
        id_list = check_jobs(id_list, queue)

        # wait 5 mins seconds before the next iteration
        time.sleep(300)

if __name__ == "__main__":
    main()