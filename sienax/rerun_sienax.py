from subprocess import check_output, check_call
from glob import glob
import csv
import os
from subprocess import Popen, Popen, PIPE
import json
import argparse
import pbr
from pbr.base import _get_output
import pandas as pd


df = pd.read_csv("/home/sf522915/rerun_mse.csv")

for _, row in df.iterrows():
    lesion = "/data/henry111"
    mse = row['mse16']
    print("THIS IS THE MSE16 COLUMN")
    if os.path.exists(_get_output(mse) +"/"+ mse + "/lesion_mni/lesion_final_new.nii.gz"):
        lesion = _get_output(mse) + "/" + mse + "/lesion_mni/lesion_final_new.nii.gz"
        sienax_out = _get_output(mse) +"/"+ mse + "/sienax_flair/"
    elif os.path.exists(_get_output(mse) +"/"+ mse + "/lesion_mni_t2/lesion_final_new.nii.gz"):
        lesion = _get_output(mse) + "/" + mse + "/lesion_mni_t2/lesion_final_new.nii.gz"
        sienax_out = _get_output(mse) +"/" + mse + "/sienax_t2/"
    else:
        print(mse, "lesion does not exist")

    if os.path.exists(lesion):
        print(mse, "lesion does exist")
        if not os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
            print(mse, "no alignment folder")

        else:
            with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
                data = json.load(data_file)
                if len(data["t1_files"]) == 0:
                    t1_file = "none"
                else:
                    t1_file = data["t1_files"][-1]
                    t1_mni = t1_file.split("alignment")[0] + "alignment/baseline_mni/" + \
                    t1_file.split('/')[-1].split('.')[0] + "_T1mni.nii.gz"
                    if os.path.exists(t1_mni):
                        proc = Popen("sienax_optibet {} -lm {} -r -d -o {}".format(t1_mni, lesion, sienax_out), stdout=PIPE, shell=True)
                        print("sienax_optibet {} -lm {} -r -d -o {}".format(t1_mni, lesion, sienax_out)) 
                        proc.wait()
                        print(mse, "sienax_completed")
