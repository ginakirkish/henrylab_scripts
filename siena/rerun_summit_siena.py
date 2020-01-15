
from glob import glob
import pandas as pd
import numpy as np
import csv
import os
from subprocess import Popen, PIPE
from pbr.base import _get_output
import json
import nibabel as nib
import shutil




df = pd.read_csv("/home/sf522915/Documents/summit_mse2.csv")



def t1_name(mse):
    if os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):

        with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
            data = json.load(data_file)
        if len(data["t1_files"]) == 0:
            t1_file1 = "none"
            #print(t1_file1)
        else:
            t1_file1 = data["t1_files"][-1]
            #print(t1_file1)
            siena = "xxx"

            cmd = ["fslhd", t1_file1]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[18:19]][0][1]
            num = output[0]

            if float(num) > 1.1:
                print(num)
                print(t1_file1)

                try:
                    siena = glob("/data/henry10/PBR_long/subjects/{0}/siena_optibet/*{1}*".format(msid,mse))[0]
                    print(siena)

                except:
                    pass
            if os.path.exists(siena):
                print("removing directory", siena)
                #shutil.rmtree(siena)







for _, row in df.iterrows():
    bl_mse = "mse" +  str(int(row["Baseline"]))
    tp1_mse = "mse" + str(int(row["12M"]))
    tp2_mse = "mse" +  str(int(row["24M"]))
    #tp3_mse = "mse" + str(int(row["120M"]))
    msid ="ms" + str(int(row["MSID"]))
    #print(bl_mse, tp1_mse)
    #print(tp1_mse, tp2_mse)
    #print(tp2_mse, tp3_mse)
    t1_name(bl_mse)
    t1_name(tp1_mse)
    t1_name(tp2_mse)
    #t1_name(tp3_mse)












"""
df = pd.read_csv("/home/sf522915/Documents/summit_rerun.csv")


for _, row in df.iterrows():
    msid = str(row["msID"])
    mse = row["mse"]
    mse1 = mse.split("_")[0]
    mse2 = mse.split("_")[1]
    T1_mse1 = row["T1_mse1"]
    T1_mse2 = row["T1_mse2"]

    print("siena_optibet", T1_mse1, T1_mse2, "-o",\
        "/data/henry10/PBR_long/subjects/" + msid+ '/siena_optibet/' + mse1 + '__' + mse2)

    cmd = ["siena_optibet", T1_mse1, T1_mse2, "-o",\
        "/data/henry10/PBR_long/subjects/" + msid+ '/siena_optibet/' + mse1 + '__' + mse2]
        proc = Popen(cmd)
        proc.wait()

"""