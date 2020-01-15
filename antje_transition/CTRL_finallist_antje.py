import numpy as np
import os
import pandas as pd
import argparse
import subprocess
from subprocess import Popen, PIPE
from glob import glob
import csv
from subprocess import check_output
import shutil
import pbr
from pbr.base import _get_output
import json
import math





df = pd.read_csv("/home/sf522915/Documents/ctrl_FINAL-antje.csv")

"""writer = open("/home/sf522915/Documents/CTRL_ARCHIVE_withacc_patientid.csv", "w")
spreadsheet = csv.DictWriter(writer,
                             fieldnames=["msid_folder","msid_mspacs", "mse", "E", "Patient_ID", "Study_Date", "Accession", "Birth_Date", "Patient_Sex", "Skyra"])
spreadsheet.writeheader()"""



for _, row in df.iterrows():
    msid = row['msid_folder']
    msid_mspac = row['msid_mspacs']
    mse = row["mse"]
    E_folder = row["E"]
    study_date = str(int(row['Study_Date']))
    print(msid, mse, E_folder)

    antje_folder =  "/data/henry6/antje/C1A/CTRL_nifti/"
    msid_dir = antje_folder + msid + '/'
    subject_dir = msid_dir + study_date
    print(subject_dir)

    if "x" in E_folder:
        print(mse, "need to copy")

        if os.path.exists(_get_output(mse) + '/' +mse + '/nii'):

            if not os.path.exists(msid_dir):
                print(msid_dir, "...making")
                os.mkdir(msid_dir)

            if not os.path.exists(subject_dir):
                print(subject_dir, "...making")
                os.mkdir(subject_dir)
            for items in os.listdir(_get_output(mse) + '/' +mse + '/nii/'):
                if items.endswith(".nii.gz"):

                    print("copying...", _get_output(mse) + '/' +mse + '/nii/' + items, subject_dir +'/' + items)
                    shutil.copy(_get_output(mse) + '/' +mse + '/nii/' + items, subject_dir + '/' + items)





    """


    if "x" in E_folder:
        #print(mse, "need to copy")


        if os.path.exists(_get_output(mse) + '/' +mse + '/nii'):
            #print(mse, "nifti exists")
            continue
        else:
            print(mse)

            try:
                dicom = glob("/working?henry_temp/PBR/dicoms/" + mse + "/E*/")
                print(dicom)
            except:
                pass"""
