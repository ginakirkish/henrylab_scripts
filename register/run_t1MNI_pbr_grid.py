from subprocess import Popen, PIPE

from glob import glob
from subprocess import Popen
import pandas as pd
import pbr
from pbr.base import _get_output
import os
import json
import subprocess

df = pd.read_csv("/home/sf522915/Documents/EPIC_notdone.csv")


for _, row in df.iterrows():
    msid ="ms" + str(row['msid']).replace("ms", "").lstrip("0")
    #mse =  str(row["mse"])
    #print(msid)
    msid_txt = "/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/msid/{0}.txt".format(msid)
    if not os.path.exists(msid_txt):
        #print(msid)
        print("    ")
    else:
        #print("pbr",msid_txt, "-w", "t1MNI_long", "-R")
        #with open(msid_txt) as f:
             #lines = f.readlines()
        lines = [line.rstrip('\n') for line in open(msid_txt)]
        for mse in lines:
            #print(mse)
            if not os.path.exists(_get_output(mse) + '/' + mse + '/alignment/baseline_mni/'):
                print(msid)
                try:
                    cmd = ["pbr",msid_txt, "-w", "t1MNI_long", "-R"]
                    print("pbr",msid_txt, "-w", "t1MNI_long", "-R")
                    Popen(cmd).wait()

                except:
                    pass

