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


df = pd.read_csv("/home/sf522915/Documents/MASTER_CLINICAL_nov27.csv")


def run_dicom(mse):
    cmd = ["ms_dcm_qr", "-t", mse.replace("mse",""), "-e", "/working/henry_temp/PBR/dicoms/"+ mse]
    Popen(cmd).wait()

def run_align(mse):
    dicom = glob("/working/henry_temp/PBR/dicoms/{}/E*/".format(mse))
    if len(dicom) < 1:
        run_dicom(mse)
    cmd = ["pbr", mse, "-w", "nifti", "align","-R"]
    Popen(cmd).wait()


def get_t1(mse):
    t1_file = ""
    #if not os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
        #run_align(mse)
    if os.path.exists(_get_output(mse1)+"/"+mse+"/alignment/status.json"):
        with open(_get_output(mse1)+"/"+mse+"/alignment/status.json") as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                t1_file = "none"
            else:
                t1_file = data["t1_files"][-1]
    return(t1_file)



def run_siena(msid, mse1, mse2): 
    pbr_long = "/data/henry10/PBR_long/subjects/"+ msid + "/siena_optibet/" + mse1 + "__" + mse2
    t1_tp0 = get_t1(mse1)
    t1_tp1 = get_t1(mse2)
    t1_1_n4 = _get_output(mse1) + '/'+mse1 + '/N4corr/'+ os.path.split(t1_tp0)[-1].replace(".nii","N4corr.nii")
    t1_2_n4 = _get_output(mse2) + '/'+mse2 + '/N4corr/'+ os.path.split(t1_tp1)[-1].replace(".nii","N4corr.nii")
    #print("T1 tp0:", t1_tp0, t1_1_n4)
    #print("*********************************")
    #print("T1 tp1:", t1_tp1, t1_2_n4)
    if os.path.exists(t1_tp0) and os.path.exists(t1_tp1):
        if not os.path.exists(t1_1_n4):
            if not os.path.exists(_get_output(mse1) + '/'+mse1 + '/N4corr/'):
                os.mkdir(_get_output(mse1) + '/'+mse1 + '/N4corr/')
            #print("N4BiasFieldCorrection", "-d", "3", "-i", t1_tp0,"-o", t1_1_n4)
            cmd = ["N4BiasFieldCorrection", "-d", "3", "-i", t1_tp0,"-o", t1_1_n4]
            Popen(cmd).wait()
        if not os.path.exists(t1_2_n4):
            if not os.path.exists(_get_output(mse2) + '/'+mse2 + '/N4corr/'):
                os.mkdir(_get_output(mse2) + '/'+mse2 + '/N4corr/')
            #print("N4BiasFieldCorrection", "-d", "3", "-i", t1_tp1,"-o", t1_2_n4)
            cmd = ["N4BiasFieldCorrection", "-d", "3", "-i",t1_tp1,"-o", t1_2_n4]
            Popen(cmd).wait()
    if os.path.exists(t1_1_n4) and os.path.exists(t1_2_n4):
        if not t1_1_n4.endswith(".gz"): 
            t1_1_n4 = t1_1_n4 + "*"
        if not t1_2_n4.endswith(".gz"): 
            t1_2_n4 = t1_2_n4 + "*"
        print("siena_optibet", t1_1_n4, t1_2_n4, "-o",pbr_long)
        try:
            shutil.rmtree(pbr_long)
        except:
            pass
        cmd = ["siena_optibet", t1_1_n4, t1_2_n4, "-o",pbr_long]
        Popen(cmd).wait()




for _, row in df.iterrows():
    msid = str(row["msid"])
    mse1 = row['mse_bl']
    mse2 = row['mse']

    siena_long = "/data/henry10/PBR_long/subjects/" + msid

    run_siena(msid, mse1, mse2)




