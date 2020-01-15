import numpy as np
import os
import pandas as pd
import argparse
from subprocess import Popen, PIPE
from glob import glob
import csv
from subprocess import check_output
import shutil
import pbr
from pbr.base import _get_output
import json
import math





df = pd.read_csv("/home/sf522915/Documents/3T_OPERA.csv")




writer = open("/home/sf522915/Documents/3T_OPERA_CHECK.csv", "w")
spreadsheet = csv.DictWriter(writer,
                             fieldnames=["msid", "mse", "ants", "lst","lst_edit", "mindcontrol",
                                        ])
spreadsheet.writeheader()



def run_ants(mse):
    print("running ants...", mse)
    cmd = ["pbr", mse, "-w", "ants", "-R"]
    Popen(cmd).wait()




for _, row in df.iterrows():
    msid ="ms" + str(row["msid"])
    mse = "mse" + str(int(row["mse"]))
    lst_edit = row["lst_edit"]
    row = {"msid": msid, "mse": mse, "lst_edit": lst_edit}
    base_dir = _get_output(mse) + '/' + mse
    if os.path.exists(base_dir + '/lst/'):
        row = {"lst": "yes"}
        if not os.path.exists(base_dir + "/antsCT"):
            run_ants(mse)
        else:
            print("ants has already been run")
    else:
        row = {"lst" : "no"}
    if os.path.exists(base_dir + '/antsCT/'):
        row = {"ants": "yes"}
    else:
        row = {"ants" : "no"}
    if os.path.exists(base_dir + '/mindcontrol/'):
        row = {"mindcontrol": "yes"}
    else:
        row = {"mindcontrol" : "no"}
spreadsheet.writerow(row)

