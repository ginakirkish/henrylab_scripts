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

def _get_output(mse):
    mse_num = int(mse[3:]) 
    if mse_num <= 4500:
        output_dir = '/data/henry7/PBR/subjects'
    else:
        output_dir = '/data/henry11/PBR/subjects'
    return output_dir
    

password = getpass("mspacman password: ")
check_call(["ms_dcm_echo", "-p", password])

folders = sorted(glob("ms*"))

writer = open("/home/sf522915/sienax_data_esha_cohort.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["msid", "date", "Scan Status", "mseID",  "old mse","sienax",
                                        "vscale", 
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)", 
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)",
                                        "lesion vol (u, mm3)","flair file","t1 file", "scanner"])
spreadsheet.writeheader()
df = pd.read_csv("/home/sf522915/esha_data.csv")

for _, row in df.iterrows():
    mse = row["FINAL MSE"]
    msid = row["msid"]
    date = row["date"]
    sienax = row["sienax"]
    old_mse = row["old mse"]
    row = {"msid": msid, "mseID": mse, "date": date, "sienax": sienax, "old mse": old_mse}
    
    if os.path.exists(_get_output(mse) +'/'+ mse + "/sienax_flair/"):
        path = _get_output(mse) +'/'+ mse + "/nii/"
        list = os.listdir(_get_output(mse)+"/"+ mse + "/sienax_flair/") # dir is your directory path
        number_files = len(list)
        if not os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
            continue
    
        with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:  
            data = json.load(data_file)
            if len(data["flair_files"]) == 0:
                flair_file = "none"
                row["flair file"] = flair_file
            else:
                flair_file = data["flair_files"][-1]
                flair_file = (flair_file.split('/')[-1])
                print(flair_file)
                row["flair file"] = flair_file

            if len(data["t1_files"]) == 0:
                t1_file = "none"
                row["t1 file"] = t1_file
            else:
                t1_file = data["t1_files"][-1]
                t1_file = (t1_file.split('/')[-1])
                print(t1_file)
                row["t1 file"] = t1_file
                
                if os.path.exists("/working/henry_temp/PBR/dicoms/" + mse):
        
                    series = t1_file.split("-")[2].lstrip("0")
                    print(series, "this is the series number")
                    if os.path.exists(glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/*.DCM".format(mse,series))[0]):
                        dcm = glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/*.DCM".format(mse,series))[0]
                        cmd = ["dcmdump", dcm, "|", "grep", "SH"]# StationName"]
                        print(cmd)
                        proc = Popen(cmd, stdout=PIPE)
                        lines = str([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]])
                        if "qb3-3t" in lines:
                            print("qb3-3t")
                            row["scanner"] = "qb3"
                        elif "SIEMENS" in lines:
                            print("SIEMENS")
                            row["scanner"] = "Skyra"
                        elif "CB3TMR"  or "CB-3TMR" in lines:
                            print("CB3TMR")
                            row["scanner"] = "CB"
                        else:
                            print(lines,"!!!!!!!!!!!!!!!!!!!!!")
                
                        
                
        if number_files > 30:
                

            report = os.path.join(_get_output(mse), mse, "sienax_flair/report.sienax")
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

            lm = os.path.join(_get_output(mse), mse, "sienax_flair/lesion_mask.nii.gz")
            img = nib.load(lm)
            data = img.get_data()
            row["lesion vol (u, mm3)"] = np.sum(data)
                
                
        else:
            print(mse, msid, "less than 30 sienax files")

    spreadsheet.writerow(row)

writer.close()
