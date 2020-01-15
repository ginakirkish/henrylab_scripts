import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
import argparse
import json
import numpy as np
import nibabel as nib
from glob import glob
from subprocess import Popen, PIPE


#df = pd.read_csv("/home/sf522915/Documents/Excluded.csv")
# df = pd.read_csv("/home/sf522915/Documents/EPIC_first_sienax_siena_NEW_Oct31.csv")
df = pd.read_csv("/home/sf522915/Documents/crtl_carlo_nico.csv")

df.columns.values[1:62]

for idx in range(len(df)):
    mse = df.loc[idx, 'mse']
    msid = df.loc[idx, 'msid']
    print(msid, mse)
    #brain = df.loc[idx, 'nBV']
    #timepoint = df.loc[idx, 'VisitType']
    #if "Baseline" in timepoint:
    sienax_bl = ""
    sienax = ""
    sienax_optibet = ""
    try:
        sienax_bl = glob(str(_get_output(mse) + '/' + mse + '/sienax*/'))[0]

        print(sienax_bl)
        print("**********", sienax_optibet)
    except:
        pass
    try:
        sienax_optibet = glob(_get_output(mse) + '/' + mse + '/sienax_optibet/ms*/report.sienax')[0]
    except:
        pass

    if os.path.exists(sienax_bl + '/report.sienax'):
        sienax_bl = sienax_bl + '/report.sienax'
        df.loc[idx, 'sienax'] = sienax_bl

        with open(sienax_bl, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if line.startswith("VSCALING"):
                    df.loc[idx, "vscale"] = line.split()[1]
                    print(mse,"vscale new",line.split()[1])
                elif line.startswith("pgrey"):
                    df.loc[idx,"cortical vol (u, mm3)"] = line.split()[2]
                elif line.startswith("vcsf"):
                    df.loc[idx,"vCSF vol (u, mm3)"] = line.split()[2]
                elif line.startswith("GREY"):
                    df.loc[idx,"GM vol (u, mm3)"] = line.split()[2]
                elif line.startswith("WHITE"):
                    df.loc[idx,"WM vol (u, mm3)"] = line.split()[2]
                elif line.startswith("BRAIN"):
                    df.loc[idx,"brain vol (u, mm3)"] = line.split()[2]
    if os.path.exists(sienax_optibet):
        df.loc[idx, 'sienax'] = sienax_optibet
        with open(sienax_optibet, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if line.startswith("VSCALING"):
                    df.loc[idx, "vscale"] = line.split()[1]
                    print(mse,"vscale new",line.split()[1])
                elif line.startswith("pgrey"):
                    df.loc[idx,"cortical vol (u, mm3)"] = line.split()[2]
                elif line.startswith("vcsf"):
                    df.loc[idx,"vCSF vol (u, mm3)"] = line.split()[2]
                elif line.startswith("GREY"):
                    df.loc[idx,"GM vol (u, mm3)"] = line.split()[2]
                elif line.startswith("WHITE"):
                    df.loc[idx,"WM vol (u, mm3)"] = line.split()[2]
                elif line.startswith("BRAIN"):
                    df.loc[idx,"brain vol (u, mm3)"] = line.split()[2]


        df.to_csv("/home/sf522915/Documents/ctrl_sienax_data3.csv")



