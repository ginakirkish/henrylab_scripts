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
import json
from subprocess import check_output, check_call
from getpass import getpass

df = pd.read_csv("/data/henry6/gina/EPIC1_imaging_exams_brainspineFINAL.csv")
password = getpass("mspacman password: ")
check_call(["ms_dcm_echo", "-p", password])

def _get_output(mse):
    mse_num = int(mse[3:])
    if mse_num <= 4500:
        output_dir = '/data/henry7/PBR/subjects'
    else:
        output_dir = '/data/henry11/PBR/subjects'
    return output_dir


def run_dicom(mse):

    cmd = ["ms_dcm_qr", "-t", mse.replace("mse", ""), "-e", "/working/henry_tmp/PBR/dicoms/" + mse, "-p", password]
    print("ms_dcm_qr -t", mse.replace("mse", ""), "-e /working/henry_tmp/PBR/dicoms/" + mse, "-p", password)
    proc = Popen(cmd)
    proc.wait()



for _, row in df.iterrows():
    mse = row["mseID"]
    mse = "mse" + mse.replace("mse", "").lstrip("0")
    msid = row["msID"]
    msid = "ms" + msid.replace("ms", "").lstrip("0")
    brain = row["BRAIN_SPINE"]
    if "Brain" in brain:
        #print(msid)
        if os.path.exists(_get_output(mse)+'/'+ mse + "/sienax_flair/"):
            #print(msid)
            continue
        elif os.path.exists(_get_output(mse)+'/'+ mse + "/sienax_t2/"):
            #print(msid)
            continue
        else:
            if not os.path.exists("/working/henry_temp/PBR/dicoms/" + mse):
                print(msid, mse, "no dicom")
                run_dicom(mse)
            else:
                for E in os.listdir("/working/henry_temp/PBR/dicoms/" + mse):
                    if not E.startswith("E"):
                        print(msid,mse ,"no dicom")
                        run_dicom(mse)
