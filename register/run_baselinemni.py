import os
from glob import glob
from subprocess import Popen, PIPE
import json
from nipype.interfaces import fsl
import argparse
from getpass import getpass
import shutil
import pandas as pd
import csv
import json
import pbr
from pbr.base import _get_output

df = pd.read_csv("/home/sf522915/EPIC1_sienax_witherror.csv")

for _, row in df.iterrows():
    msid = row['msID']
    msid = "ms" + msid.replace("ms", "").lstrip("0")
    mse = row["mseID"]


    if os.path.exists(_get_output(mse) + "/" + mse + "/sienax_t2/") or os.path.exists(_get_output(mse)+ "/" + mse + "/sienax_flair/")\
                      or not os.path.exists(_get_output(mse) + "/" + mse + "/alignment/status.json")\
                      or os.path.exists(_get_output(mse) + "/" + mse + "/sienax"):
        print(mse, "THIS SIENAX FILE EXISTS or NO ALIGNMENT FILE")
        continue
    else: 
        status = _get_output(mse) + "/" + mse + "/alignment/status.json"
        if not os.path.exists(status):
            continue
        with open(status) as data_file:
            data = json.load(data_file)

            if len(data["t1_files"]) == 0:
                  t1_file = "none"

            else:
                t1_file = data["t1_files"][-1]

            t1_mni = _get_output(mse) + "/" + mse + "/alignment/baseline_mni/" + os.path.split(t1_file)[1].split(".")[0] +  "_T1mni.nii.gz"
            print(t1_mni)
            if not os.path.exists(t1_mni):
                if os.path.exists(_get_output(mse) + "/" + mse + "/alignment/baseline_mni/"):
                    os.rmdir(_get_output(mse) + "/" + mse + "/alignment/baseline_mni/")
                print("/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/gina/" + msid + ".txt")
                if os.path.exists("/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/gina/" + msid + ".txt"): 
                        
                    cmd = ["pbr", "/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/gina/" + msid + ".txt", "-w", "t1MNI_long", "-R"]
                    print(cmd)
                    proc = Popen(cmd)
                    proc.wait()
            


