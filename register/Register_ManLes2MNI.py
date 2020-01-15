


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

def get_t2(mse):
    with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
        data = json.load(data_file)
        if len(data["t2_files"]) > 0:
            t2_file = data["t2_files"][-1].split("/")[-1]
            t2_file = _get_output(mse) + '/' + mse + "/alignment/baseline_mni/" + t2_file.replace(".n", "_T1mni.n")
    return t2_file

def make_dir(dir):
    if not os.path.exists(dir):
        print("making...", dir)
        os.mkdir(dir)

def register_mni(c):
    df = pd.read_csv("{}".format(c))
    for _, row in df.iterrows():
        timepoint = row["timepoint"]
        if timepoint == "Baseline":
            print(timepoint)
            ms = row['msid']
            pbr_long = "/data/henry10/PBR_long/subjects/" + ms
            msid ="ms" + row['msid'].replace("ms", "").zfill(4)
            mse = str(row["mse"])
            mse_pbr = _get_output(mse) + '/' + mse
            ms_bl_les = bl_les + msid + "_baseline_lesions.nii.gz"
            ms_brain = sienax_noles + msid + "/I_brain.nii.gz"
            bl_sienax = ""
            print(msid, mse)

            try:
                bl_sienax = glob(mse_pbr+ '/sienax/*/I_brain.nii.gz')
                print(bl_sienax)
            except:
                pass

            if len(bl_sienax) < 1:
                print("NEED TO RUN", mse)
            else:

                lesion_dir = mse_pbr + "/lesion_mni_t2/"

                make_dir(lesion_dir)
                make_dir(pbr_long)
                make_dir(pbr_long + "/MNI/")

                #if not os.path.exists(pbr_long + "/MNI/lesion_"+ mse + ".nii.gz"):

                if os.path.exists(mse_pbr): #+ "/sienax_manles/lesion_mask.nii.gz"):
                    print(mse, "manual segmented lesion mask has not yet been registered for this subject")


                    #cmd = ["flirt", "-interp", "nearestneighbour","-dof", "6", "-in", ms_brain, "-ref", bl_sienax[-1],"-omat", lesion_dir +  mse + ".mat" ]
                    print("flirt", "-interp", "nearestneighbour","-dof", "6", "-in", ms_brain, "-ref", bl_sienax[-1],"-omat", lesion_dir +  mse + ".mat")
                    #Popen(cmd).wait()


                    #cmd = ["flirt", "-init",lesion_dir +  mse + ".mat" , "-applyxfm", "-in", ms_bl_les, "-ref", bl_sienax[-1], "-out", pbr_long + "/MNI/lesion_"+ mse + ".nii.gz"]
                    print("flirt", "-init",lesion_dir +  mse + ".mat" , "-applyxfm", "-in", ms_bl_les, "-ref", bl_sienax[-1], "-out", pbr_long + "/MNI/lesion_"+ mse + ".nii.gz")
                    #Popen(cmd).wait()


                    #cmd = ["sienax_optibet",get_t1(mse), "-lm",pbr_long + "/MNI/lesion_"+ mse + ".nii.gz", "-r", "-d", "-o", mse_pbr + "/sienax_manles/" ]
                    print("sienax_optibet",get_t1(mse), "-lm",pbr_long + "/MNI/lesion_"+ mse + ".nii.gz", "-r", "-d", "-o", mse_pbr + "/sienax_manles/")
                    #Popen(cmd).wait()

                    print(mse_pbr + "/sienax_manles/I_stdmaskbrain_pve_2.nii.gz",pbr_long + "/MNI/" + "wm_" + mse + ".nii.gz")
                    print(mse_pbr + "/sienax_manles/I_stdmaskbrain_pve_1.nii.gz",pbr_long + "/MNI/" + "gm_" + mse + ".nii.gz")
                    print(get_t2(mse),pbr_long + "/MNI/" + get_t2(mse).split("/")[-1])

                    print("***********************************************")

                    #shutil.copyfile(mse_pbr + "/sienax_manles/I_stdmaskbrain_pve_2.nii.gz",pbr_long + "/MNI/" + "wm_" + mse + ".nii.gz")
                    #shutil.copyfile(mse_pbr + "/sienax_manles/I_stdmaskbrain_pve_1.nii.gz",pbr_long + "/MNI/" + "gm_" + mse + ".nii.gz")
                    #shutil.copyfile(get_t2(mse),pbr_long + "/MNI/" + get_t2(mse).split("/")[-1] )



if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code checks for the dicom, nifti, align pipelines and rund them given an mse')
    parser.add_argument('-i', help = 'mse')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    print(c)
    register_mni(c)
