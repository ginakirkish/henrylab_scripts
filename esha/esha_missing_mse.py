import json
import numpy as np
import os
import pandas as pd
import argparse
from os.path import join
import csv
import pbr
from subprocess import Popen, PIPE
from glob import glob
import csv
import matplotlib.pyplot as plt
from subprocess import check_output
import shutil
from getpass import getpass
from nipype.utils.filemanip import load_json
from pbr.workflows.nifti_conversion.utils import description_renamer
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
df3 = pd.read_csv("/home/sf522915/esha_mse.csv")
PBR_base1 = "/data/henry7/PBR/subjects/"
PBR_base2 = "/data/henry11/PBR/subjects/"
password = getpass("mspacman password:")


def _get_output(mse):
    mse_num = int(mse[3:]) 
    if mse_num <= 4500:
        output_dir = '/data/henry7/PBR/subjects'
    else:
        output_dir = '/data/henry11/PBR/subjects'
    return output_dir

def get_all_mse(msid):
    cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid]
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[5:]]
    tmp = pd.DataFrame(lines, columns=["mse", "date"])
    tmp["mse"] = "mse"+tmp.mse
    tmp["msid"] = msid
    return tmp

def get_modalityt1(mse, nii_type="FLAIR"):
    output = pd.DataFrame(index=None)
    num = mse.split("mse")[-1]
    cmd = ["ms_dcm_exam_info", "-t", num]
    proc = Popen(cmd, stdout=PIPE)
    #lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[8:]]

    lines = [description_renamer(" ".join(l.decode("utf-8").split()[1:-1])) for l in proc.stdout.readlines()[8:]]
    #print(lines, "lines")
    if nii_type:
        #print(nii_type)
        files = filter_files(lines, nii_type, heuristic)
        #print(mse, "t1 exists")
        output["nii"] = files
        
    else:
        output["nii"] = lines
        print(mse, "NO T1")
    output["mse"] = mse
    return output


def filter_files(descrip,nii_type, heuristic):
    output = []
    for i, desc in enumerate(descrip):
        if desc in list(heuristic.keys()):
            if heuristic[desc] == nii_type:
                 print(mse, "FLAIR")
                 output.append(desc)
            else:
                 print(mse, "no FLAIR")
    return output



for _, row in df3.iterrows():
    mse = str(row["mse"])
    msid =  row["msid"].replace("ms","")
    date = row["date"]
    cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid, "--dcm_dates"]
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[5:]]
    tmp = pd.DataFrame(lines, columns=["mse", "date"])
    #print(tmp)
    tmp["msid"] = msid
    tmp = pd.DataFrame(lines, columns=["mse", "date"])
    tmp["msid"] = msid
    mse = tmp["mse"]
    date2 = tmp["date"]
    for _, row in tmp.iterrows():
        mse = "mse" + row["mse"]
        date2 = row["date"]
        if str(date) == (date2):
            #print(msid, mse, date2, date)
            #print(_get_output(mse) +"/"+mse+"/alignment/status.json")
            if not os.path.exists(_get_output(mse) +"/"+mse+"/alignment/status.json"):
                #print(msid, mse, date, "NO alignment")
                continue
            else:
                with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
                    data = json.load(data_file)
                    if len(data["t1_files"]) == 0:
                        t1_file = "none"
                    else:
                       t1_file = data["t1_files"][-1]
                       print(msid, mse, date, t1_file)



    '''num = mse.split("mse")[-1]
    cmd = ["ms_get_patient_id", "--exam_id", num]
    proc = Popen(cmd, stdout=PIPE)
    msid = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][7:8][0][2]
    #print(mse)
    proc = Popen("ms_get_phi --examID {} --studyDate -p {}".format(mse, password), stdout=PIPE, shell=True)
    proc.wait()
    res = proc.stdout.readlines()
    output = [r.decode("utf-8") for r in res]
    date = str(output[10:11][0])[-10:]'''
    #print(date)
    #get_modalityt1(mse)

    """for _, row in df3.iterrows():   
        mse = row["mse"]
    msid = row["msid"].replace("ms","")
    cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid, "--dcm_dates"]
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[5:]]
    print(lines)
    
    tmp = pd.DataFrame(lines, columns=["mse", "date"])
    #print(tmp)
    tmp["msid"] = msid
    tmp = pd.DataFrame(lines, columns=["mse", "date"])
    tmp["msid"] = msid
    mse = tmp["mse"]
    date2 = tmp["date"]
    for _, row in tmp.iterrows():
        mse = row["mse"]
        date2 = row["date"]
        if str(date1) == (date2):
            print(msid, mse, date2, date1)


    if os.path.exists(_get_output(mse) +'/'+mse + "/sienax_flair/" ):
        print("sienax flair")#(mse) #, mse, "sienax_flair")
        #continue
    elif os.path.exists(_get_output(mse) +'/'+ mse+ "/sienax_t2/"):
        print("sienax_t2") # (mse) #, mse, "sienax_t2")
        #continue
    elif os.path.exists(_get_output(mse) +'/'+mse+ "/lesion_mni_t2/"):
        print("lesion_mni_t2") #(mse) #, mse, "lesion_mni_t2")
        #continue
    elif os.path.exists(_get_output(mse) +'/'+mse+ "/alignment/baseline_mni/"):
        print("baseline_mni")#mse) #, mse, "baseline_mni")
    elif os.path.exists(_get_output(mse) +'/'+mse+ "/alignment/"):
        print("alignment") #mse) #, mse, "alignment")
    elif os.path.exists(_get_output(mse) +'/'+mse+ "/nii/"):
        print("nifti") #(mse) # , mse, "nii")
    elif os.path.exists("/working/henry_temp/PBR/dicoms/" + mse):
        print("dicom") #)mse) #, mse, "dicom")
    else: 
        print("no dicom")(mse) #, mse, "no dicom")"""
