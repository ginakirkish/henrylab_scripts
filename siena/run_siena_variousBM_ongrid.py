from glob import glob
import pandas as pd
import numpy as np
import csv
import os
from subprocess import Popen, PIPE, check_call
from pbr.base import _get_output
import json
import nibabel as nib
import argparse
pbr_long = "/data/henry12/siena_BM/"


def run_siena(mse1, mse2):

    #print("python", "/data/henry6/gina/scripts/grid_submit.py", "'{0} {1} {2} {3} {4} {5}'".format("python", "/data/henry6/gina/scripts/MONSTR_EPICatlas_siena.py", "-mse1", mse1, "-mse2", mse2))
    #print("python", "/data/henry6/gina/scripts/grid_submit.py", "'{0} {1} {2} {3} {4} {5}'".format("python", "/data/henry6/gina/scripts/warp_BM_siena.py", "-mse1", mse1, "-mse2", mse2))


    #try:
        #check_call("python",  "/data/henry6/gina/scripts/MONSTR_EPICatlas.py", "-mse1", mse1, "-mse2", mse2)
        #print("python", "/data/henry6/gina/scripts/warp_BM_siena.py", "-mse1", mse1, "-mse2", mse2)
        #check_call("python", "/data/henry6/gina/scripts/warp_BM_siena.py", "-mse1", mse1, "-mse2", mse2)
    print("python",  "/data/henry6/gina/scripts/MONSTR_EPICatlas_siena.py", "-mse1", mse1, "-mse2", mse2)
    cmd = ["python",  "/data/henry6/gina/scripts/MONSTR_EPICatlas_siena.py", "-mse1", mse1, "-mse2", mse2]
    Popen.wait(cmd)
    #except:
        #pass
    #print("*********")


if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab siena values given a csv (with mse and msid) and an output csv')
    parser.add_argument('-i', help = 'csv containing the msid and mse')

    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv('{0}'.format(c))
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        msid = "ms" + msid.replace("ms", "").lstrip("0")
        mse1 = df.loc[idx,'mse1']
        mse2 = df.loc[idx, 'mse2']
        run_siena(msid, mse1, mse2)

        """pbvc = df.loc[idx, "siena_MONSTR"]
        #pbvc = df.loc[idx, 'siena_fnirtBM_fromBL']
        pbvc = str(pbvc)
        if len(pbvc) == 3:
            print("No siena value:", pbvc)
            mse1 = str(mse1)
            mse2 = str(mse2)
            if not len(mse1) == 3:
                print(mse1)
                #run_siena(mse1, mse2)
