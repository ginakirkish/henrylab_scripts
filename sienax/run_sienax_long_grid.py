
import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json
from subprocess import Popen, PIPE
from getpass import getpass
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
import shutil
import pandas as pd

df = pd.read_csv("/home/sf522915/Documents/EPIC_APRIL2019_MASTER-align.csv")
#all_epic_info_March2019.csv")
pbr_long = "/data/henry10/PBR_long/subjects/"

def get_flair():
    status = "{}/{}/nii.status.json".format(_get_output(mse), mse, )

for idx in range(len(df)):
    msid = "ms" + str(df.loc[idx, 'msid']).replace("ms", "").lstrip("0")
    mse = "mse" + str(df.loc[idx, 'mse']).replace("mse", "").lstrip("0")
    visit = df.loc[idx, 'VisitType']
    sienax = df.loc[idx, 'sienax']
    resample_sienax = df.loc[idx, "resample_sienax"]
    #if visit == "Baseline":
    if str(resample_sienax) == "False":
        msid_txt = "/data/henry6/gina/epic_text/" + msid + ".txt"
        print("python", "/data/henry6/gina/scripts/grid_submit.py","'{0} {1} {2} {3} {4} {5}'".format("pbr", msid_txt, "-w", "t1MNI_long", "FLAIRles_long","-R" ) )
        #cmd = ["pbr", msid_txt, "-w", "t1MNI_long", "-ps", "Rosie1313", "-R"]
        #print(cmd)
        #Popen(cmd).wait()

        #cmd = ["pbr", msid_txt, "-w", "FLAIRles_long", "-R" ]
        #print(cmd)
        #Popen(cmd).wait()





