
import os
import pandas as pd

from subprocess import Popen, PIPE

from pbr.base import _get_output
import json


df = pd.read_csv("/home/sf522915/Documents/siena_rerun.csv")





for _, row in df.iterrows():
    msid = row["msID"]
    mse = row["siena"]
    mse1 = mse.split("_")[0]
    mse2 = mse.split("_")[-1]
    print(mse1, mse2)
    if not os.path.exists(_get_output(mse1)+"/"+mse1+"/alignment/status.json") or \
    not os.path.exists(_get_output(mse2)+"/"+mse2+"/alignment/status.json"):
        continue

    with open(_get_output(mse1)+"/"+mse1+"/alignment/status.json") as data_file:
        data = json.load(data_file)
    if len(data["t1_files"]) == 0:
        t1_file1 = "none"

    else:
        t1_file1 = data["t1_files"][-1]

        t1_base = _get_output(mse1) + "/" + mse1 + "/alignment/baseline_mni/"
        series = t1_file1.split('-')[2]
        print(t1_base)
        print(series)
        for t1_1 in os.listdir(t1_base):
            if series in t1_1:
                t1_file1FINAL = t1_base +"/"+ t1_1
                print(t1_file1)

    with open(_get_output(mse2)+"/"+mse2+"/alignment/status.json") as data_file:
        data = json.load(data_file)
    if len(data["t1_files"]) == 0:
        t1_file2 = "none"

    else:
        t1_file2 = data["t1_files"][-1]

        t1_base2 = _get_output(mse2) + "/" + mse2 + "/alignment/baseline_mni/"
        series2 = t1_file2.split('-')[2]
        print(t1_base2)
        print(series2)
        for t1_2 in os.listdir(t1_base2):
            if series2 in t1_2:
                t1_file2FINAL = t1_base2 +"/"+ t1_2
                print(t1_file2)


    #if not os.path.exists("/data/henry11/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0]):
        #os.mkdir("/data/henry11/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0])
    #if not os.path.exists("/data/henry11/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0]+ '/' + mse1 + '_to_' + mse2):


    print("siena_optibet", t1_file1FINAL, t1_file2FINAL, "-o",\
                  "/data/henry11/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0]+ '/' + mse1 + '_to_' + mse2)

    cmd = ["siena_optibet", t1_file1FINAL, t1_file2FINAL, "-o",\
                  "/data/henry11/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0] + '/' + mse1 + '_to_' + mse2]
    proc = Popen(cmd)
    proc.wait()
