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
from pbr.base import _get_output 

mse_list = ["mse12280", "mse12283", "mse3217","mse11999","mse12000",
"mse12001",
"mse12002",
"mse2867",
"mse8124",
"mse12003",
"mse12004",
"mse12005",
"mse2936",
"mse11993",
"mse11994",
"mse11998",
"mse2927",
"mse4249",
"mse12006",
"mse12007",
"mse12009",
"mse12010",
"mse12011",
"mse12256",
"mse12266",
"mse12275",
"mse12277",
"mse12278",
"mse12279",
"mse6417",
"mse12285",
"mse12289",
"mse12290",
"mse2958",
"mse3053",
"mse12291",
"mse12293",
"mse2961",
"mse2962",
"mse3119",
"mse5617",
"mse12512",
"mse12513",
"mse12514"]

for mse in mse_list:
    print(mse)
    status = _get_output(mse)+'/' + mse + "/alignment/status.json"

    if os.path.exists(status):
        print(status)
        with open(status) as data_file:
            data = json.load(data_file)

            if len(data["t1_files"]) == 0:
                #print("no {0} t1 files".format(tp))
                t1_file = "none"

            else:
                t1_file = data["t1_files"][-1]
                t1_mni = _get_output(mse) + '/'+ mse + "/alignment/baseline_mni/" + os.path.split(t1_file)[1].split(".")[0] +  "_T1mni.nii.gz"
                print(t1_mni)
                if os.path.exists(t1_mni):
                     msid = t1_file.split("-")[0]
                     print(t1_mni) 
                     if not os.path.exists(_get_output(mse) + "/" + mse + "/sienax/"): 
                         cmd = ["sienax_optibet",t1_mni, "-r", "-d", "-o", _get_output(mse) + "/" + mse + "/sienax/"]
                         print("Running SIENAX....", cmd)
                         proc = Popen(cmd)
                         proc.wait()
    """else:
         cmd = ["pbr",mse, "-w", "align", "-R"]
         print("Running SIENAX....", cmd)
         proc = Popen(cmd)
         proc.wait()"""

