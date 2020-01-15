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
    try: 
 
        sienax_bl = glob(str(_get_output(mse) + '/' + mse + '/sienax_*/'))[0]

        print(sienax_bl)
        if os.path.exists(sienax_bl):
            print(sienax_bl)
            
            df.loc[idx, "sienax"]  = sienax_bl

            #df.loc[idx, 'sienax_bl'] = "sienax_bl"
            report = sienax_bl + '/report.sienax'
            with open(report, "r") as f:
                    lines = [line.strip() for line in f.readlines()]
                    for line in lines:
                        if not len(line) >= 1:
                            continue
                        if line.startswith("VSCALING"):
                            try:
                                df.loc[idx, "vscale"] = line.split()[1]
                                print(mse,"vscale new",line.split()[1])
                            except:
                                pass
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
                    try:

                        lm = sienax_bl +  "/lesion_mask.nii.gz"
                        img = nib.load(lm)
                        data = img.get_data()
                        df.loc[idx, "lesion vol (u, mm3)"] = np.sum(data)
                        print(mse, np.sum(data))
                    except:
                        pass

                    df.to_csv("/home/sf522915/Documents/ctrl_sienax_data.csv")


    except:

        pass
