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
import subprocess

def run_pbr_nifti(mse):
    #cmd = ["python", "/data/henry6/gina/scripts/run_pbr_troubleshoot_errors.py", mse]
    cmd = ["pbr", mse, "-w", "nifti", "-R"]
    #print(mse)
    x = 1
    #proc = Popen(cmd)
    #proc.wait()

def run_siena(mse1, mse2):
    try:
        siena_long = glob("/data/henry10/PBR_long/subjects/{0}/siena_optibet/*{1}*{2}*/B_optiBET_brain_mask.nii.gz".format(msid, mse1, mse2))[0]
        print(siena_long)
    except:
        print("pbr", mse1, mse2, "-w", "siena_optibet", "-R")
    #print(siena_long)
    """if len(siena_long) < 2:
        #print(msid, mse1, mse2)
        siena = "/data/henry10/PBR_long/subjects/{0}/siena_optibet/{1}__{2}".format(msid, mse1, mse2)
        #print(siena)
        if not os.path.exists("/data/henry10/PBR_long/subjects/{0}/".format(msid)):
            os.mkdir("/data/henry10/PBR_long/subjects/{0}/".format(msid))
        if not os.path.exists("/data/henry10/PBR_long/subjects/{0}/siena_optibet/".format(msid)):
            os.mkdir("/data/henry10/PBR_long/subjects/{0}/siena_optibet/".format(msid))

        if not os.path.exists(siena + '/B_optiBET_brain_mask.nii.gz'):
            #os.mkdir(siena)
            mse_pbr1 = _get_output(mse1) + '/' + mse1 + '/alignment/status.json'
            t1_1 = ""
            if os.path.exists(mse_pbr1):
                with open(mse_pbr1) as data_file:
                    data1 = json.load(data_file)
                if len(data1["t1_files"]) > 0:
                    t1_1 = data1["t1_files"][-1]
            mse_pbr2 = _get_output(mse2) + '/' + mse2 + '/alignment/status.json'
            if os.path.exists(mse_pbr2):
                with open(mse_pbr2) as data_file:
                    data2 = json.load(data_file)
                if len(data2["t1_files"]) > 0:
                    t1_2 = data2["t1_files"][-1]
                    if len(t1_1) >1:
                        print("siena_optibet", t1_1, t1_2, "-d", "-o", "/data/henry10/PBR_long/subjects/{0}/siena_optibet/{1}__{2}".format(msid,mse1, mse2))"""

            #print("pbr", mse1, mse2, "-w", "siena_optibet", "-R")
            #cmd = ["pbr", mse1, mse2, "-w", "siena_optibet", "-R"]
            #proc = Popen(cmd)
            #proc.wait()
        #subprocess.check_call(["python", "/data/henry6/gina/scripts/grid_submit.py","{0}".format("pbr "+ mse1 + " "+ mse2 +" -w siena_optibet -R")])
        #print(["python", "/data/henry6/gina/scripts/grid_submit.py","{0}".format("pbr "+ mse1 + " "+ mse2 +" -w siena_optibet -R")])

    """
    try:
        siena_long = glob("/data/henry10/PBR_long/subjects/{0}/siena_optibet/*{1}*{2}*".format(msid, mse1, mse2))[0]
        #print(siena_long)
    except:
        #print(mse1, mse2, "NEED TO RUN")
        #print("/data/henry10/PBR_long/subjects/" + msid + '/' + mse1 + "_to_" + mse2)
        print('python /data/henry6/gina/scripts/grid_submit.py "{0}"'.format("pbr " + mse1 + " " + mse2 + " -w siena_optibet -R"))
        #cmd = ["pbr", mse1, mse2, "-w", "siena_optibet", "-R"]
        #print("pbr", mse1, mse2, "-w", "siena_optibet", "-R")
        #subprocess.check_call(["python", "/data/henry6/gina/scripts/grid_submit.py","{0}".format("pbr "+ mse1 + " "+ mse2 +" -w siena_optibet -R")])
        #proc = Popen(cmd)
        #proc.wait()"""

#df = pd.read_csv("/home/sf522915/Documents/noFLAIR_sienaxBESTnew.csv")
#df = pd.read_csv("/home/sf522915/Documents/EPIC2_carlo.csv")
#df = pd.read_csv("/home/sf522915/Documents/EPIC_siena.csv") #1_sienax_clincalPASAT_merged_Oct17.csv")
df = pd.read_csv("/home/sf522915/Documents/msid_dec11.csv") # EPIC1_sienax_dataCOMBINED_scannerinfo_Nov302018.csv")

ind = 0 
for _, row in df.iterrows():
    msid ="ms" +  str(row["msid"]).replace("ms", "").lstrip("0")
    
    msid_txt = "/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/msid/" + msid + ".txt"
    ind = 0 
    with open(msid_txt) as f:
        #content = f.readlines()
        content = f.read().splitlines()
        size = len(content) -1
        index = 0
        while index < size:
            index += 1
            #print(content[index-1], content[index])
            mse1 = content[index-1]
            mse2 = content[index]
            run_siena(mse1,mse2)
            """



            if not os.path.exists(_get_output(mse1) + '/' + mse1 + '/nii/'):
                run_pbr_nifti(mse1)
            if not os.path.exists(_get_output(mse2) + '/' + mse2 + '/nii/'):
                run_pbr_nifti(mse2)
            else:
                run_siena(mse1, mse2)"""


