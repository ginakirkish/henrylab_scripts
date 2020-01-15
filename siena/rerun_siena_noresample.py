
import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json
from subprocess import Popen, PIPE
from getpass import getpass
#from subprocess import check_output, check_call
import json
#import pandas as pd
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
import pandas as pd
import shutil

df = pd.read_csv("/home/sf522915/Documents/MASTER-EPIC1_all_epic_info_MAY.csv")
pbr_long = "/data/henry10/PBR_long/subjects/"


def check_for_resampling_align(file):
    check = ""
    try:
        cmd = ["fslstats", file, "-R" ]
        proc = Popen(cmd, stdout=PIPE)
        max = str(float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][-1]))
        if max.endswith(".0"):
            check = True
        else:
            check = False
    except:
        pass
    return check

def get_t1(mse):
    t1_file = ""
    get_align = "{}/{}/alignment/status.json".format(_get_output(mse), mse)
    if os.path.exists(get_align):
        with open(get_align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1_file = data["t1_files"][-1].replace("_reorient", "")
    return t1_file



for idx in range(len(df)):
    msid = "ms" + str(df.loc[idx, 'msid']).replace("ms", "").lstrip("0")
    mse = "mse" + str(df.loc[idx, 'mse']).replace("mse", "").lstrip("0")
    siena = glob("{}/{}/siena_optibet/{}_*".format(pbr_long, msid, mse))
    for items in siena:
        A_file = items + "/A.nii.gz"
        B_file = items + "/B.nii.gz"
        if os.path.exists(A_file) and os.path.exists(B_file):

            #shutil.copyfile(A_file, A_file.replace(".nii", "_new.nii"))
            #shutil.copyfile(B_file, B_file.replace(".nii", "_new.nii"))
            A_check = str(check_for_resampling_align(A_file.replace(".nii","_new.nii")))
            B_check = str(check_for_resampling_align(B_file.replace(".nii", "_new.nii")))
            if A_check == "False" or B_check == "False":
                #shutil.rmtree(items)
                #pbr_long = "/data/henry13/PBR_long/subjects/"
                mse2 = "mse" + A_file.split("mse")[2].replace("_","").split("/")[0]
                pbr_long2 = "/data/henry12/PBR_long/subjects/"
                output =  pbr_long2 + msid + '/siena_optibet/' + mse +"__"+ mse2
                """#print("siena_optibet",2et_t1(mse), get_t1(mse2), "-o", output)"""
                if not os.path.exists(pbr_long2 + msid):
                    os.mkdir(pbr_long2 + msid)
                    print("mkdir", pbr_long2 + msid)
                if not os.path.exists(pbr_long2 + msid + '/siena_optibet/'):
                    os.mkdir(pbr_long2 + msid + '/siena_optibet/')
                    print("mkdir", pbr_long2 + msid + '/siena_optibet/')
                if os.path.exists(output + '/report.html'):
                    print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("siena_optibet", get_t1(mse), get_t1(mse2), "-o", output))
                    #cmd = ["siena_optibet", get_t1(mse), get_t1(mse2), "-o", output]
                    #Popen(cmd).wait()
                #print(A_file, B_file)
                """try:
                    t1 = get_t1(mse)
                    t1 = t1.split('/')[-1].split(".nii.gz")[0]
                    work = glob("/working/henry_temp/keshavan/pipeline_siena_*{}*ms*".format(t1))[0]
                    mse2 = "mse" + A_file.split("mse")[2].replace("_","").split("/")[0]
                    #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {} {}"'.format("pbr", mse, mse2, "-w", "siena_optibet", "-R"))
                    os.remove(work)
                    print(work)
                except:
                    pass"""

                #print(A_file)
                #mse2 = "mse" + A_file.split("mse")[2].replace("_","").split("/")[0]
                #cmd = ["pbr", mse, mse2, "-w", "siena_optibet", "-R"]
                #print("pbr", mse, mse2, "-w", "siena_optibet", "-R")
                #os.remove(A_file.replace(".nii","_new.nii"))
                #os.remove(B_file.replace(".nii","_new.nii"))
                #Popen(cmd).wait()


