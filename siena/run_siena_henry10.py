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
import pbr 
from pbr.base import _get_output 
import json 


df = pd.read_csv("/home/sf522915/Documents/EPIC2_carlo.csv")

ind = 0 
for _, row in df.iterrows():
    msid ="ms" + str(row["msid"])
    msid = "/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/gina/" + msid + ".txt"
    ind = 0 
    with open(msid) as f:
        #content = f.readlines()
        content = f.read().splitlines()
        size = len(content) -1
        index = 0
        while index < size:
            index += 1
            print(msid)
            print(content[index-1], content[index])
            mse1 = content[index-1]
            mse2 = content[index]

            if not os.path.exists(_get_output(mse1)+"/"+mse1+"/alignment/status.json") or \
            not os.path.exists(_get_output(mse2)+"/"+mse2+"/alignment/status.json"):
                continue

            with open(_get_output(mse1)+"/"+mse1+"/alignment/status.json") as data_file:
                data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                t1_file1 = "none"

            else:
                t1_file1 = data["t1_files"][-1]
                #print(t1_file1)
                #t1_file1 = t1_file1.split("alignment")[0] + "alignment/baseline_mni/" + \
                #t1_file1.split('/')[-1].split('.')[0] + "_T1mni.nii.gz"

            with open(_get_output(mse2)+"/"+mse2+"/alignment/status.json") as data_file:
                data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                t1_file2 = "none"

            else:
                t1_file2 = data["t1_files"][-1]
                #t1_file2 =  t1_file2.split("alignment")[0] + "alignment/baseline_mni/" + \
                #t1_file2.split('/')[-1].split('.')[0] + "_T1mni.nii.gz"


            if not os.path.exists("/data/henry10/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0]):
                os.mkdir("/data/henry10/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0])
            if not os.path.exists("/data/henry10/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0] + '/' + mse1 + '_to_' + mse2): 
                print("siena_optibet", t1_file1, t1_file2, "-o",\
                "/data/henry10/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0] + '/' + mse1 + '_to_' + mse2)
                cmd = ["siena_optibet", t1_file1, t1_file2, "-o",\
                          "/data/henry10/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0] + '/' + mse1 + '_to_' + mse2]
                proc = Popen(cmd)
                proc.wait()
                break
