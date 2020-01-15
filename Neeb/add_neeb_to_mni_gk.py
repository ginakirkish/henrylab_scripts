from subprocess import check_call
from glob import glob
import pandas as pd
import argparse
import os
import pbr
from pbr.base import _get_output
import json
from subprocess import Popen, PIPE

parser = argparse.ArgumentParser()
parser.add_argument("--msid", nargs="+")
args = parser.parse_args()

#df = pd.read_excel("/data/henry6/study_reBUILD/reBUILD_processing_paths.xlsx", sheetname="Neeb")
df = pd.read_csv("/home/sf522915/Documents/reBUILD_Neeb_EduAmit.csv")

transforms = sorted(glob("/data/pelletier1/study_reBUILD/registrations/nonlinear/*warp.nii.gz"))
workdir = "/data/pelletier1/study_reBUILD/neeb_to_mni/" #"/data/pelletier1/study_reBUILD/MNI_WM_analysis/Neeb_MNI/"
ref = os.environ["FSLDIR"]+"/data/standard/MNI152_T1_2mm_brain.nii.gz"
output =  "/data/pelletier1/study_reBUILD/neeb_to_mni/"


for _, row in df.iterrows():
    msid = row["msid"]
    mse = row["mse"]
    print(msid, mse)
    original_path = "/working/henry_temp/sd_data/" + msid +'/'+ mse + '/Neeb/'
    print(original_path)
    try:
        brain = glob(original_path + "/T1Maps/*.nii.gz")[0]
        print(brain)
    except:
        pass
    if os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
        with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
            data = json.load(data_file)
        if len(data["t1_files"]) == 0:
            t1_file = "none"
        else:
            t1_file = data["t1_files"][-1]
            print(t1_file)
        if len(data["t1_mask"]) >= 1:
            brain_mask = data["t1_mask"][-1]
            print(brain_mask)

    #t1 = t1_file.replace(".nii", "_bet.nii")
    t1 = t1_file
    #cmd = ["fslmaths", t1_file, "-mul", brain_mask, t1]
    #Popen(cmd).wait()
    #print(cmd)

    t1_to_dti = output + msid + '-' + mse + "_mprage_to_neeb.mat"
    dti_to_t1 = output + msid + '-' + mse + "_neeb_to_mprage.mat"
    warped = os.path.join(workdir, "%s-%s-%s.nii.gz" %(msid, mse, "warpedmni"))
    print(warped, "FINAL SCAN")

    if not os.path.exists(warped):
        try:

            cmd = ["flirt", "-searchrx", "-180", "180", "-searchry", "-180", "180", "-searchrz", "-180", "180",
                            "-cost", "normmi", "-in", t1, "-ref", brain, "-omat", t1_to_dti, "-out", t1_to_dti[:-4]+"_affine.nii.gz"]
            print(cmd)
            Popen(cmd).wait()


            cmd = ["flirt", "-searchrx", "-180", "180", "-searchry", "-180", "180", "-searchrz", "-180", "180",
                            "-cost", "normmi", "-in", brain, "-ref", t1, "-omat", dti_to_t1, "-out", t1_to_dti[:-4]+"_affine.nii.gz"]
            print(cmd)
            Popen(cmd).wait()

            cmd = ["fnirt", "--in="+t1, "--aff="+t1_to_dti, "--ref="+brain, "--iout="+t1_to_dti[:-4]+"_affine.nii.gz",
                            "--cout="+t1_to_dti[:-4]+"_warp.nii.gz"]
            print(cmd)
            Popen(cmd).wait()


            cmd = ["invwarp", "-r", t1, "-w", t1_to_dti[:-4]+"_warp.nii.gz", "-o", dti_to_t1[:-4]+"_warp.nii.gz"]
            print(cmd)
            Popen(cmd).wait()

            cmd = ["convert_xfm", "-omat", dti_to_t1, "-inverse", t1_to_dti]
            Popen(cmd).wait()
            print(cmd)

            metric = original_path + "/Myelin/MyelinMapsSmooth/MyelinMap_Smoothed_08.nii.gz"
            print(metric)
            output =  os.path.join(workdir, "%s-%s-%s-to_T1.nii.gz" %(msid, mse, "Myelin"))
            print(output)

            check_call(["applywarp", "-i", metric, "-r", t1, "-w", dti_to_t1[:-4]+"_warp.nii.gz", "-o", output])
            print("applywarp", "-i", metric, "-r", t1, "-w", dti_to_t1[:-4]+"_warp.nii.gz", "-o", output)
            # check_call(["flirt", "-in", image, "-applyxfm", "-init", dti_to_t1, "-ref", t1,
            #             "-out", output])
            affines = _get_output(mse)+"/"+mse+"/alignment/mni_affine.mat"
            othert1 =  _get_output(mse)+"/"+mse+"/alignment/mni_angulated/" + t1_file.split('/')[-1].replace(".nii", "_trans.nii")
            warp = _get_output(mse)+"/"+mse+"/alignment/mni_angulated/" + t1_file.split('/')[-1].replace(".nii", "_brain_flirt.nii")

            check_call(["flirt", "-in", output, "-applyxfm", "-init", affines, "-ref", t1, "-out", output])
            print("flirt", "-in", output, "-applyxfm", "-init", affines, "-ref", t1, "-out", output)
            check_call(["fslreorient2std", output, output])
            print("flirt", "-in", output, "-applyxfm", "-init", affines, "-ref", t1, "-out", output)
            check_call(["applywarp", "-i", output, "-r", ref, "-o", warped])
            print("applywarp", "-i", output, "-r", ref, "-o", warped)
        except:
            pass


