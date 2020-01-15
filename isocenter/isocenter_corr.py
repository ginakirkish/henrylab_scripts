
import pandas as pd
import argparse
import json
import numpy as np
import nibabel as nib
from glob import glob
import os
import pbr
from subprocess import Popen, PIPE
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
from pbr.base import _get_output
import re


def filter_files(descrip,nii_type, heuristic):
    output = []
    for i, desc in enumerate(descrip):
        if desc in list(heuristic.keys()):
            if heuristic[desc] == nii_type:
                 output.append(desc)
    return output



def get_sq_name(mse):
    try:

        with open(_get_output(mse)+"/"+mse+"/nii/status.json") as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                print("")
                sq = ""
            else:
                t1_file = data["t1_files"][-1]
                sq = t1_file.split('-')[2:3][0].lstrip("0")
                print(sq)
            return sq
    except:
        pass


def get_dicom_hdr(c,out):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        mse = df.loc[idx, 'mse']
        print(mse)
        if mse.startswith("mse"):

            dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/E*.DCM".format(mse,get_sq_name(mse)))
            if len(dicom) >=1:
                dicom = dicom[0]
                print(dicom)

                cmd = ["dicom_hdr", "-sexinfo", dicom] #, "|","grep", "sDistortionCorrFilter.ucMode"]
                proc = Popen(cmd, stdout=PIPE)
                output =[l.decode('latin-1').split() for l in proc.stdout.readlines()[:]]
                for line in output:
                    if len(line) >= 1:

                            newline = line[0]

                            if "ucTablePositioningMode" in newline:
                                uctable = line[2]
                                print("ucTable:", uctable)
                                df.loc[idx, "ucTablePositioningMode"] = uctable
                            if "DistortionCorrFilter.ucMode" in newline:
                                dist = line[2]
                                print("DistortionCorrFilter:", dist)
                                df.loc[idx, "DistortionCorrFilter"] = dist
                            if "lScanRegionPosTra" in newline:
                                scanreg = line[2]
                                print("lScanRegionPosTra:", scanreg)
                                df.loc[idx, "lScanRegionPosTra"] = scanreg


        df.to_csv("{0}".format(out))

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the Distortion Corr Filter and uc Table Positioning Mode')
    parser.add_argument('-i', help = 'csv containing the mse')
    parser.add_argument('-o', help = 'output csv')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    get_dicom_hdr(c,out)







