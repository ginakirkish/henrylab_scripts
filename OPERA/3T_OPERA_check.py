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


text_file = "/home/sf522915/Documents/mse_OPERA_3T.txt"


def run_nifti(mse):
    cmd = ["pbr", mse, "-w", "nifti", "-R"]
    Popen(cmd).wait()
    run_align(mse)

def run_align(mse):
    cmd = ["pbr", mse, "-w", "align", "-R"]
    Popen(cmd).wait()


def run_pbr(mse):
    if os.path.exists(_get_output(mse) + '/' + mse + "/lst/"):
        shutil.rmtree(_get_output(mse) + '/' + mse + "/lst/")
    #os.mkdir(_get_output(mse) + '/' + mse + '/lst/')
    cmd = ["pbr", mse, "-w", "lst", "-R"]
    Popen(cmd).wait()

    if not os.path.exists(_get_output(mse) + "/" + mse + "/mindcontrol/"):
        print(mse, "This scan is not on mindcontrol")
    else:
        print(mse, "this path is on mindcontrol")
"""
        cmd = ["mc_up", "-e", "-production", "-s", mse]
        Popen(cmd).wait()
        print(cmd)
        print(mse, "THIS SCAN IS NOW ON MINDCONTROL")
"""
working = "/working/henry_temp/PBR/dicoms/"

with open(text_file,'r') as f:
    timepoints = f.readlines()
    timepoints = timepoints[::-1]
    for timepoint in timepoints:
        mse = "mse" + timepoint.replace("\n","")
        if os.path.exists(working + "/{0}".format(mse)):
            try:
                dicom = glob(working + "/{0}/E*".format(mse))[0]
                #print("DICOM DIRECTORY:", dicom)
            except:
                print(mse, "no dicom")
                pass
        if not os.path.exists(_get_output(mse) + '/' + mse + "/nii/"):
            print(mse, "NO NIFTI")
            #run_nifti(mse)
        elif not os.path.exists(_get_output(mse) + '/' + mse + "/alignment/"):
            print(mse, "no alignment")
            #run_nifti(mse)
        elif not os.path.exists(_get_output(mse) + '/' + mse + "/alignment/baseline_mni/"):
            print(mse,"no baseline mni")
        else:
            print(mse, "everything is HERE WEEEEEEEEEEEEEEEEEE")

        #print(mse)
        """if not os.path.exists(_get_output(mse) + '/' + mse + "/lst/lpa/"):
            #print(_get_output(mse) + '/' + mse + "/lst/")
            #print("LST IS COMLPETED")
            print(_get_output(mse) + "/" + mse + "/mindcontrol/")
            if not os.path.exists(_get_output(mse) + "/" + mse + "/mindcontrol/"):
                #print(mse, "mindcontrol")
                cmd = ["mc_up", "-e", "production", "-s", str(mse)]
                #print("mc_up", "-e", "production", "-s", str(mse))
                #Popen(cmd).wait()
            else:
                print(mse, "mindcontrol is completed")"""
        #else:
            #print(mse, "path does not exist")
            #print(_get_output(mse) + '/' + mse + "/lst/")
            #run_pbr(mse)

