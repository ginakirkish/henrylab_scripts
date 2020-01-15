


import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json
from subprocess import Popen, PIPE
from getpass import getpass
import csv
import pandas as pd
import shutil


bl_les = "/data/henry6/alyssa/lesions_reg/manual_lesions/baseline/"
sienax_noles =  "/data/henry6/alyssa/no_lesions_sienax/baseline/"

def get_t1(mse):
    with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1].split("/")[-1]
            t1_file = _get_output(mse) + '/' + mse + "/alignment/baseline_mni/" + t1_file.replace(".ni", "_T1mni.ni")
    return t1_file



def make_dir(dir):
    if not os.path.exists(dir):
        print("making...", dir)
        os.mkdir(dir)

def register_mni(c):
    df = pd.read_csv("{}".format(c))
    for _, row in df.iterrows():
        ms = row['msid']
        mse = str(row["mse"])
        mse_pbr = _get_output(mse) + '/' + mse
        lesion_dir = mse_pbr + "/lesion_mni_t2/"
        #print(ms, mse, lesion_dir)
        #print("sienax_optibet",get_t1(mse), "-lm",lesion_dir + "lesion_final_new.nii.gz" , "-r", "-d", "-o", mse_pbr + "/sienax_t2/" )

        if not os.path.exists(mse_pbr + "/sienax_t2/"):
            print(mse)
            cmd = ["sienax_optibet",get_t1(mse), "-lm",lesion_dir + "lesion_final_new.nii.gz" , "-r", "-d", "-o", mse_pbr + "/sienax_t2/" ]
            print("sienax_optibet",get_t1(mse), "-lm",lesion_dir + "lesion_final_new.nii.gz" , "-r", "-d", "-o", mse_pbr + "/sienax_t2/" )
            Popen(cmd).wait()
            print("***********************************************")



if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code checks for the dicom, nifti, align pipelines and rund them given an mse')
    parser.add_argument('-i', help = 'mse')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    print(c)
    register_mni(c)
