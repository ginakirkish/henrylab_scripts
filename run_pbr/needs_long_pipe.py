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



def get_align(mse):
    t1_file = ""
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    if os.path.exists(align):
        print("")
        #print(mse, "alignment has been completed")
    else:
        print("python", "/data/henry6/gina/scripts/grid_submit.py", "'{} {} {} {}'".format("python", "/data/henry6/gina/scripts/run_pbr_troubleshoot_errors.py", "-i", mse))
        #cmd = ["python", "/data/henry6/gina/scripts/run_pbr_troubleshoot_errors.py", "-i", mse]
        #Popen(cmd).wait()


def get_t1(mse):
    t1_file = ""
    get_align = "{}/{}/alignment/status.json".format(_get_output(mse), mse)
    if os.path.exists(get_align):
        with open(get_align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1_file = data["t1_files"][-1].replace("_reorient", "")
    return t1_file

def run_t1mni(msid, mse):
    txt = "/data/henry6/gina/epic_text/" + msid + ".txt"
    baseline_mni = glob("{}/{}/alignment/baseline_mni/ms*.nii.gz".format(_get_output(mse),mse))
    if len(baseline_mni)> 0:
        baseline_mni = baseline_mni[0]
        #print(baseline_mni, "YAY")
    else:
        #print(baseline_mni, "DOES NOT EXIST")
        print("python", "/data/henry6/gina/scripts/grid_submit.py", "'{} {} {} {} {}'".format("pbr", txt, "-w", "t1MNI_long", "-R"))
        cmd = ["pbr", txt, "-w", "t1MNI_long", "-R"]
        #Popen(cmd).wait()


def check_les(msid, mse):
    txt = "/data/henry6/gina/epic_text/" + msid + ".txt"
    les = glob("{}/{}/lesion_origspace_*/lesion.nii.gz".format(_get_output(mse),mse))
    if len(les)> 0:
        les = les[0]
        #print(les, "YAY")
    else:
        print("python", "/data/henry6/gina/scripts/grid_submit.py", "'{} {} {} {} {}'".format("pbr", txt, "-w", "FLAIRles_long", "-R"))
        cmd = ["pbr", txt, "-w", "FLAIRles_long", "-R"]
        #Popen(cmd).wait()

def check_sienax(mse):
    sienax = glob("{}/{}/sienaxorig_*/lesion.nii.gz".format(_get_output(mse),mse))
    if len(sienax)> 0:
        sienax = sienax[0]
        #print(sienax, "YAY")
    else:
        print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("pbr",mse, "-w", "sienax_optibet", "-R"))
        cmd = ["pbr",mse, "-w", "sienax_optibet", "-R"]
        #Popen(cmd).wait()

def run_long(c):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        msid = "ms" + str(df.loc[idx, 'msid']).replace("ms", "").lstrip("0")
        mse = "mse" + str(df.loc[idx, 'mse']).replace("mse", "").lstrip("0")
        vscale = df.loc[idx, "Vscale"]
        if len(str(vscale)) < 4:
            print(msid, mse)
            print(vscale)
            get_align(mse)
            run_t1mni(msid, mse)
            check_les(msid, mse)
            check_sienax(mse)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    run_long(c)
