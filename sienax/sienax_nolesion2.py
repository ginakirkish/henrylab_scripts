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

#df = pd.read_csv("/home/sf522915/EPIC1_sienax_witherror.csv")
df = pd.read_csv("/home/sf522915/Documents/sienax_nolesion.csv")
for _, row in df.iterrows():
    msid = row['msID']
    msid = "ms" + msid.replace("ms", "").lstrip("0")
    mse = row["mseID"]
    if not os.path.exists(_get_output(mse) + "/" + mse + "/sienax"): 
        print(_get_output(mse) + "/" + mse + "/sienax")
        status = _get_output(mse) + "/" + mse + "/alignment/status.json"
        print(status)
        if not os.path.exists(status):
            continue
        else:
            with open(status) as data_file:
                data = json.load(data_file)

                if len(data["t1_files"]) == 0:
                    t1_file = "none"

                else:
                    t1_file = data["t1_files"][-1]

                    t1 = os.path.split(t1_file.split(".nii.gz")[0])[-1]
                    cmd = ["sienax_optibet",t1_file, "-r", "-d", "-o", _get_output(mse) + "/" + mse + "/sienax/" + t1]
                    print("Running SIENAX....", cmd)
                    proc = Popen(cmd)
                    proc.wait()
            


