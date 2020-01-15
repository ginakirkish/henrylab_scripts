from subprocess import check_output, check_call
import nibabel as nib
import numpy as np
import os
import pandas as pd
import argparse
from os.path import join
import csv
from subprocess import Popen, PIPE
from glob import glob
import csv
import matplotlib.pyplot as plt
from subprocess import check_output
import shutil
from getpass import getpass
import json
from pbr.base import _get_output

"""def _get_output(mse):
    mse_num = int(mse[3:]) 
    if mse_num <= 4500:
        output_dir = '/data/henry7/PBR/subjects'
    else:
        output_dir = '/data/henry11/PBR/subjects'
    return output_dir"""
    

password = getpass("mspacman password: ")
check_call(["ms_dcm_echo", "-p", password])

folders = sorted(glob("ms*"))

writer = open("/home/sf522915/sienax_data_reginacontrol.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["name", "fname", "msid", "date", "mseID",
                                        "vscale", 
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)", 
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)"])
spreadsheet.writeheader()
df = pd.read_csv("/home/sf522915/regins_ctrl.csv")

for _, row in df.iterrows():
    mse = row["mse"]
    msid = row["msid"]
    date = row["date"]
    name = row["Name"]
    fname = row["First Name"]
    row = {"name": name, "fname": fname, "msid": msid, "mseID": mse, "date": date}
    
    if os.path.exists(_get_output(mse) +'/'+ mse + "/sienax_nolesion/"):
        path = _get_output(mse) +'/'+ mse + "/nii/"
        list = os.listdir(_get_output(mse)+"/"+ mse + "/sienax_nolesion/") # dir is your directory path
        number_files = len(list)
        if number_files > 30:
                

            report = os.path.join(_get_output(mse), mse, "sienax_nolesion/report.sienax")
            with open(report, "r") as f:
                lines = [line.strip() for line in f.readlines()]
                for line in lines:
                    if line.startswith("VSCALING"):
                        row["vscale"] =  line.split()[1]
                    elif line.startswith("pgrey"):
                        row["cortical vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("vcsf"):
                        row["vCSF vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("GREY"):
                        row["GM vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("WHITE"):
                        row["WM vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("BRAIN"):
                        row["brain vol (u, mm3)"] = line.split()[2]
               
        else:
            print(mse, msid, "less than 30 sienax files")

    spreadsheet.writerow(row)

writer.close()

