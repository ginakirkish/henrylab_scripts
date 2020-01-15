import os
from glob import glob
from subprocess import Popen, PIPE
import json
from nipype.interfaces import fsl
from nipype.interfaces.fsl import RobustFOV, Reorient2Std
from nipype.interfaces.c3 import C3dAffineTool
import argparse
from getpass import getpass
import shutil
import pandas as pd
import csv

base_dir = "/data/henry7/PBR/subjects/"

for mse in os.listdir(base_dir):
    if os.path.exists(base_dir + mse + "/sienax/"):
        status = base_dir + mse + "/alignment/status.json"
        #print(mse)
        if not os.path.exists(status):
            continue
        with open(status) as data_file:
            data = json.load(data_file)

            if len(data["t1_files"]) == 0:
                #print("no {0} t1 files".format(tp))
                t1_file = "none"

            else:
                t1_file = data["t1_files"][-1]
            
            #print(t1_file)
            t1_mni = base_dir + mse + "/alignment/baseline_mni/" + os.path.split(t1_file)[1].split(".")[0] +  "_T1mni.nii.gz"
            #print(t1_mni)
            if not os.path.exists(t1_mni):
                msid = t1_file.split("-")[0]
                #print(t1_mni, "does not exist")
                
            else:
                if os.path.exists(base_dir + mse + "/lesion_mni/"):
                    for lesion in os.listdir(base_dir + mse + "/lesion_mni/"):
                        if lesion.startswith("lesion_prob_map"):
                            lesion_file = base_dir + mse + "/lesion_mni/" + lesion
                            print(lesion_file, t1_mni)
                            if not os.path.exists(base_dir + "/" + mse + "/sienax_flair/"): 
                                shutil.rmtree(base_dir + "/" + mse + "/sienax/")
                                cmd = ["sienax_optibet",t1_mni, "-lm", lesion_file , "-r", "-d", "-o", base_dir + "/" + mse + "/sienax_flair/"]
                                print("Running SIENAX....", cmd)
                                proc = Popen(cmd)
                                proc.wait()
            
