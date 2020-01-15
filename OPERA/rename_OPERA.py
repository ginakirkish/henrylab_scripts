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

df = pd.read_csv("/home/sf522915/Documents/OPERA.csv")

for _, row in df.iterrows():
    msid = "ms" + str(row['msid'])
    mse = "mse" + str(row["mse"])
    date = str(row["date"])
    scanner = str(row["scanner"])
    opera_id = str(row["OPERA_ID"])
    yr = str(row["yr"])
    #print(msid, mse, date,scanner, opera_id, yr)

    if not os.path.exists(_get_output(mse) +'/' + mse + "/nii/"):
        print(msid, mse, yr)
    else:
        new_nii = msid + "_" + mse + "_" + opera_id + "_" + yr
        #print(new_nii)
        print(_get_output(mse) +'/' + mse + "/nii/", "/data/henry6/OPERA/all_scans/" + new_nii)
        shutil.copytree(_get_output(mse) +'/' + mse + "/nii/", "/data/henry6/OPERA/all_scans/" + new_nii)
        #print(_get_output(mse) + "/" + mse + "/nii/", "DOES NOT EXIST")
        #print("/working/henry_tmp/PBR/dicoms/" + mse)
    #if not os.path.exists("/working/henry_tmp/PBR/dicoms/" + mse):
        #print("/working/henry_tmp/PBR/dicoms/" + mse, "DOES NOT EXIST")
    #else:
        #print(mse, "THIS MSE EXISTS")
