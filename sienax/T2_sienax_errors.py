from subprocess import check_output, check_call
from glob import glob
import csv
import os
from subprocess import Popen, Popen, PIPE
import json
import argparse

base_dir = "/data/henry7/PBR/subjects/"

for mse in os.listdir(base_dir):
    lesion = base_dir + mse + "/lesion_mni_t2/lesion_final_new.nii.gz"
    if os.path.exists(lesion):
        if not os.path.exists(base_dir + mse + "/sienax_t2/lesion_mask.nii.gz"):
            if os.path.exists(base_dir+mse +"/alignment/status.json"):
                with open(base_dir+mse +"/alignment/status.json") as data_file:  
                    data = json.load(data_file)
       
                    if len(data["t1_files"]) == 0:
                        continue
                    else:
                        t1_file = data["t1_files"][-1]
                        print(mse)
                        t1_mni = t1_file.split("alignment")[0] + "alignment/baseline_mni/" + \
                        t1_file.split('/')[-1].split('.')[0] + "_T1mni.nii.gz"
                        sienax_out = base_dir + mse + "/sienax_t2"
                        if not os.path.exists(sienax_out):
                            os.mkdir(sienax_out)
                            proc = Popen("/data/henry6/keshavan/bin/sienax_optibet {} -lm {} -r -d -o {}".format(t1_mni, lesion, sienax_out), stdout=PIPE, shell=True)
                            print("sienax_optibet {} -lm {} -r -d -o {}".format(t1_mni, lesion, sienax_out))
                            proc.wait()
                            print(mse, "sienax_completed")
