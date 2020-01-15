import os
from glob import glob
from subprocess import Popen, PIPE
import json
from nipype.interfaces import fsl
import argparse
from getpass import getpass
import shutil
import pandas as pd
import csv
import json
import pbr
from pbr.base import _get_output

df = pd.read_csv("/home/sf522915/EPIC1_sienax_witherror.csv")

for _, row in df.iterrows():
    msid = row['msID']
    msid = "ms" + msid.replace("ms", "").lstrip("0")
    mse = row["mseID"]
    


    if os.path.exists(_get_output(mse) + "/" + mse + "/sienax/"):
        for data in os.listdir(_get_output(mse) + "/" + mse + "/sienax/"): 
            if data.startswith("data"):
                
                for henry in os.listdir(_get_output(mse) + "/" + mse + "/sienax/" + data):
                    new = _get_output(mse) + "/" + mse + "/sienax/" + data +'/'+ henry + "/PBR/subjects/" + mse + '/alignment/'
                    for t1 in os.listdir(new):
                        print(new + t1, _get_output(mse) + "/" + mse + "/sienax/"+ t1)
                        os.rename(new + t1, _get_output(mse) + "/" + mse + "/sienax/"+ t1)
"""                    
                    base = _get_output(mse) + "/" + mse + "/alignment/"
                    for t1 in os.listdir(base): 
                        
              
                        print(t1)
                        print(data)
                        print(_get_output(mse) + "/" + mse + "/sienax/" + data, _get_output(mse) + "/" + mse + "/sienax/" + t1)
                        #os.rename(_get_output(mse) + "/" + mse + "/sienax/" + data, _get_output(mse) + "/" + mse + "/sienax/"+data.split("/")[-1])

     print(mse, "THIS SIENAX FILE EXISTS or NO ALIGNMENT FILE")
        continue
    else: 
        status = _get_output(mse) + "/" + mse + "/alignment/status.json"
        if not os.path.exists(status):
            continue
        with open(status) as data_file:
            data = json.load(data_file)

            if len(data["t1_files"]) == 0:
                  t1_file = "none"

            else:
                t1_file = data["t1_files"][-1]

            t1_mni = _get_output(mse) + "/" + mse + "/alignment/baseline_mni/" + os.path.split(t1_file)[1].split(".")[0] +  "_T1mni.nii.gz"
            #print(t1_mni)
            if os.path.exists(t1_mni):
                cmd = ["sienax_optibet",t1_mni, "-r", "-d", "-o", _get_output(mse) + "/" + mse + "/sienax/" + t1_file.split(".nii.gz")[0]]
                print("Running SIENAX....", cmd)
                proc = Popen(cmd)
                proc.wait()
"""
            


