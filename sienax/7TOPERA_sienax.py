import numpy as np
import os
import pandas as pd
import argparse
from subprocess import Popen, PIPE
from glob import glob
import csv
from subprocess import check_output
import shutil
import pbr
from pbr.base import _get_output
import json
import math


text_file = "/home/sf522915/Documents/OPERA_7T.txt"


def run_sienax(mse, msid):
    lesion_mask = "/data/henry10/PBR_long/subjects/" + msid + "/t1manseg_lesions/lesion_mni.nii.gz"
    if os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):


        with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
            data = json.load(data_file)

            if len(data["t1_files"]) >= 1:
                t1_file = os.path.split(data["t1_files"][0])[-1]
                t1_file = _get_output(mse) + '/' + mse + '/alignment/baseline_mni/' + t1_file.replace(".nii", "_T1mni.nii")
                cmd = ["sienax", t1_file, "-lm", lesion_mask, "-r", "-d", '-o', _get_output(mse) + "/" + mse + '/sienax_t1manualseg' ]
                print(cmd)
                Popen(cmd).wait()


with open(text_file,'r') as f:
    timepoints = f.readlines()
    timepoints = timepoints[::]

    for timepoint in timepoints:
        mse = timepoint.replace("\n","")
        cmd = ["ms_get_patient_id","--exam_id", mse.replace("mse", "")]
        print(cmd)
        proc = Popen(cmd, stdout=PIPE)
        msid= [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][3:][4][2]
        print("msid is....", msid)

        run_sienax(mse, msid)
        """
        if os.path.exists(_get_output(mse) + '/' + mse + "/lesion_mni.nii.gz"):
            print(_get_output(mse) + '/' + mse + "/lesion_mni.nii.gz")
            print("lesion mni is completed")

            #os.mkdir("/data/henry10/PBR_long/subjects/" + msid + "/t1manseg_lesions/")
            print("/data/henry10/PBR_long/subjects/" + msid + "/t1manseg_lesions/")
            #shutil.copyfile(_get_output(mse) + '/' + mse + "/lesion_mni.nii.gz", "/data/henry10/PBR_long/subjects/" + msid + "/t1manseg_lesions/lesion_mni.nii.gz" )
        """