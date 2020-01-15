import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json, uuid
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from subprocess import Popen, PIPE, check_call, check_output
import pandas as pd
import shutil

pbr_dir = ["/data/henry7/PBR/subjects/", "/data/henry11/PBR/subjects/"]

def run_nifti_align(mse):
    cmd = ["pbr", mse, "-w","nifti","align","-R"]
    Popen(cmd).wait()

def get_t1(mse):
    t1_file = ""
    if mse.startswith("mse") and not mse == "mse5756":
        get_align = "{}/{}/alignment/status.json".format(_get_output(mse), mse)
        if os.path.exists(get_align):
            with open(get_align) as data_file:
                data = json.load(data_file)
                if len(data["t1_files"]) > 0:
                    t1_file = data["t1_files"][-1]
                    if "DESPOT" in t1_file:
                        run_nifti_align(mse)
    return t1_file

def check_int(t1):
    check = ""
    try:
        cmd = ["fslstats", t1, "-R" ]
        proc = Popen(cmd, stdout=PIPE)
        max = str(float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][-1]))
        #print(max)

        if max.endswith(".0"):
            print(max, "True")
            check = True
        else:
            check = False
            #print(max, "False")
    except:
        pass
    return check


for path in pbr_dir:
    for mse in os.listdir(path):
        try:
            t1 = get_t1(mse)
            if os.path.exists(t1):
                if check_int(t1) == "False":
                    run_nifti_align(mse)
        except:
            pass
