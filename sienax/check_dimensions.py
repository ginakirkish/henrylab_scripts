
import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
from getpass import getpass
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
import pandas as pd
import shutil
import nibabel as nib
import numpy as np



def get_t1(mse):
    t1 = ""
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    if os.path.exists(align):
        with open(align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1 = data["t1_files"][-1]
    return t1

def get_sienax(mse):
    sienax = lesion = ""
    sienax_optibet = glob("/{0}/{1}/sienax_optibet/ms*/I_brain.nii.gz".format(_get_output(mse),mse))
    sienax_fl = "/{0}/{1}/sienaxorig_flair/I_brain.nii.gz".format(_get_output(mse),mse)
    sienax_t2 = "/{0}/{1}/sienaxorig_t2/I_brain.nii.gz".format(_get_output(mse),mse)
    if len(sienax_optibet) >= 1:
        sienax = sienax_optibet[0]
        lesion = sienax.replace("I_brain.nii.gz","lesion_mask.nii.gz")
    elif os.path.exists(sienax_fl):
        sienax = sienax_fl
        lesion = sienax.replace("I_brain.nii.gz","lesion_mask.nii.gz")
    elif os.path.exists(sienax_t2):
        sienax = sienax_t2
        lesion = sienax.replace("I_brain.nii.gz","lesion_mask.nii.gz")
    else:
        sienax = ""
        lesion = ""
    return [sienax, lesion]


def get_les_origspace(mse):
    les_origspace = ""
    les_orig = glob("{}/{}/lesion_origspace*/lesion*.nii.gz".format(_get_output(mse),mse))
    if len(les_orig)>0:
        les_origspace = les_orig[0]
    return les_origspace

def check_dim(file):
    dim1, dim2, dim3, dim = "","","",""
    if os.path.exists(file):
        cmd = ["fslhd", file]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]

        for l in output:
            if "dim1" in l and not "pix" in l:
                dim1 = l[-1]
            if "dim2" in l and not "pix" in l:
                dim2 = l[-1]
            if "dim3" in l and not "pix" in l:
                dim3 = l[-1]
        dim = dim1 + "-" + dim2 + "-" + dim3
        print(dim1, dim2, dim3)
        print(dim)
    return dim

def get_lst_long(msid):
    lst = ""
    lst_long = glob("/data/henry10/PBR_long/subjects/{}/lst_edit_sienax/mse*/I_brain.nii.gz".format(msid))
    if len(lst_long)>0:
        lst = lst_long[0]
    return lst



def get_msid(mse):
    cmd = ["ms_get_patient_id", "--exam_id", mse.split("mse")[1]]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][-1][2].split("'")[-1]
    return output


def write_csv(c, out):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx, 'mse']
        #msid = get_msid(mse)
        print(msid, mse)
        t1 = get_t1(mse)
        s = get_sienax(mse)
        sienax = s[0]
        lesion = s[1]
        df.loc[idx, "msid"] = msid
        df.loc[idx, "t1 dimensions"] = check_dim(t1)
        df.loc[idx, "sienax dim"] = check_dim(sienax)
        df.loc[idx, "lesion dim"] = check_dim(lesion)
        df.loc[idx, "lesion origspace dim"] = check_dim(get_les_origspace(mse))
        df.loc[idx, "lst long dim"] = check_dim(get_lst_long(msid))


    df.to_csv("{}".format(out))

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    write_csv(c, out)