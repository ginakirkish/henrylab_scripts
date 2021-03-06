import numpy as np
import os
import pandas as pd
import argparse
from subprocess import Popen, PIPE
from glob import glob
import csv
import matplotlib.pyplot as plt
from subprocess import check_output
import shutil
import pbr
from pbr.base import _get_output
import json
mni ="/netopt/rhel7/versions/fsl/fsl_5.0.10/data/standard/MNI152lin_T1_1mm.nii.gz"

def run_siena(mse1, mse2):
    if not os.path.exists(_get_output(mse1)+"/"+mse1+"/nii/status.json"):
        #print(mse1, "NO ALIGNMENT FOLDER")
        print("             ")
    elif not os.path.exists(_get_output(mse2)+"/"+mse2+"/nii/status.json"):
        #print(mse2, "NO ALIGNMENT FOLDER")
        print("         ")
    else:
        with open(_get_output(mse1)+"/"+mse1+"/nii/status.json") as data_file:
            data = json.load(data_file)
        if len(data["t1_files"]) == 0:
            t1_file1 = "none"

        else:
            t1_file1 = data["t1_files"][-1]
            cmd = ["fslreorient2std", t1_file1, t1_file1]
            #Popen(cmd).wait()


        with open(_get_output(mse2)+"/"+mse2+"/nii/status.json") as data_file:
            data = json.load(data_file)
        if len(data["t1_files"]) == 0:
            t1_file2 = "none"

        else:
            t1_file2 = data["t1_files"][-1]
            cmd = ["fslreorient2std", t1_file2, t1_file2]
            #Popen(cmd).wait()

        if not os.path.exists("/data/henry10/PBR_long/subjects/" + msid):
            os.mkdir("/data/henry10/PBR_long/subjects/" + msid)



        print("siena_optibet", t1_file1, t1_file2, "-o",\
                 "/data/henry10/PBR_long/subjects/" + msid+ '/siena_optibet/' + mse1 + '__' + mse2)
        print("                   ")

        #cmd = ["siena_optibet", t1_file1, t1_file2, "-o",\
                 #"/data/henry10/PBR_long/subjects/" + msid+ '/siena_optibet/' + mse1 + '__' + mse2]
        #proc = Popen(cmd)
        #proc.wait()

df = pd.read_csv("/home/sf522915/Documents/summit_mse2.csv")



def t1_name(mse):
    if not os.path.exists(_get_output(mse)+"/"+mse+"/nii/status.json"):
        #print(mse, "NO ALIGNMENT FOLDER")
        print("           ")
    with open(_get_output(mse)+"/"+mse+"/nii/status.json") as data_file:
        data = json.load(data_file)
    if len(data["t1_files"]) == 0:
        t1_file1 = "none"
        #print(t1_file1)
    else:
        t1_file1 = data["t1_files"][-1]
        #print(t1_file1)


def check_for_pbvc(siena, mse1, mse2):
    siena_report = siena + "/report.siena"
    if os.path.exists(siena_report):
        #print(siena_report)
        with open(siena_report, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            if len(lines) < 75:
                print(siena_report)
                #os.rmdir(siena)
                run_siena(mse1, mse2)







for _, row in df.iterrows():
    bl_mse = "mse" +  str(int(row["Baseline"]))
    tp1_mse = "mse" + str(int(row["12M"]))
    tp2_mse = "mse" +  str(int(row["24M"]))
    #tp3_mse = "mse" + str(int(row["120M"]))
    msid = "ms" + str(row["MSID"])
    #print(bl_mse, tp1_mse)
    #print(tp1_mse, tp2_mse)
    #print(tp2_mse, tp3_mse)
    #t1_name(bl_mse)
    #t1_name(tp1_mse)
    #t1_name(tp2_mse)
    #t1_name(tp3_mse)

    try:
        siena1 = glob("/data/henry10/PBR_long/subjects/{0}/siena_optibet/*{1}*{2}*".format(msid,bl_mse, tp1_mse))[0]
        #check_for_pbvc(siena1, bl_mse, tp1_mse)

    except:
        #print(msid, bl_mse, tp1_mse)
        mse1 = bl_mse
        mse2 = tp1_mse
        run_siena(mse1, mse2)
        pass

    try:
        siena2 = glob("/data/henry10/PBR_long/subjects/{0}/siena_optibet/*{1}*{2}*".format(msid,tp1_mse, tp2_mse))[0]
        #print(siena2)
        #check_for_pbvc(siena2, tp1_mse, tp2_mse)

    except:
        #print(msid, tp1_mse, tp2_mse)
        mse1 = tp1_mse
        mse2 = tp2_mse
        run_siena(mse1, mse2)
        pass

    """try:
        siena3= glob("/data/henry10/PBR_long/subjects/{0}/siena_optibet/*{1}*{2}*".format(msid,tp2_mse))[0]
        #print(siena3 + "/report.html")
        check_for_pbvc(siena3, tp2_mse, tp3_mse)

    except:
        #print(msid, tp2_mse, tp3_mse)
        mse1 = tp2_mse
        mse2 = tp3_mse
        run_siena(mse1, mse2)
        pass"""







        #print(siena1)

