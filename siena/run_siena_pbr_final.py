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
        #print(siena_long)
    except:
        print("python", "/data/henry6/gina/scripts/grid_submit.py",'"pbr', mse1, mse2, "-w", "siena_optibet", '-R"')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab siena values given a csv (with mse and msid) and an output csv')
    parser.add_argument('-i', help = 'csv containing the msid and mse')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))
    ind = 0 
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse1_old = df.loc[idx,'mse']
        
    
        msid_txt = "/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/msid/" + msid + ".txt"
        ind = 0 
        with open(msid_txt) as f:
            content = f.read().splitlines()
            size = len(content) -1
            index = 0
            while index < size:
                index += 1
                #print(content[index-1], content[index])
                
                mse1 = content[index-1]
                mse2 = content[index]
                if mse1_old == mse1: 
                    #print(mse1, mse2)
                    run_siena(mse1, mse2)

