
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
from nipype.algorithms.metrics import ErrorMap, Distance, Overlap, Similarity

def get_t1(mse):
    t1 = ""
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    if os.path.exists(align):
        with open(align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1 = data["t1_files"][-1]
    return t1

def make_lesion(mse):
    les_out = "{}/{}/new_lesion/".format(_get_output(mse), mse)
    sienax_flair_mni = "{}/{}/sienax_flair/lesion_mask.nii.gz".format(_get_output(mse),mse)
    sienax_t2_mni = "{}/{}/sienax_t2/lesion_mask.nii.gz".format(_get_output(mse),mse)
    inv_affine = "{}/{}/alignment/mni_affine_inv.mat".format(_get_output(mse),mse)
    if os.path.exists(sienax_flair_mni):
        s = sienax_flair_mni
    elif os.path.exists(sienax_t2_mni):
        s = sienax_t2_mni
    else:
        s = ""
    if os.path.exists(inv_affine):
        les_out = "{}/{}/new_lesion/".format(_get_output(mse), mse)
        if not os.path.exists(les_out):
            os.mkdir(les_out)
        cmd = ["flirt", "-init", inv_affine, "-applyxfm", "-in", s, "-ref", get_t1(mse), "-o",les_out + "/lesion.nii.gz" ]
        Popen(cmd).wait()
    return les_out + "/lesion.nii.gz"


def nifti_diff(lesion_new, les_old):
    cmd = ["nifti1_tool", "-disp_hdr","-infiles",lesion_new, les_old]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    print(output)
    return str(output)

def write_csv(c, out):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx, 'mse']
        #mse = "mse1827"
        #msid = get_msid(mse)
        print(msid, mse)
        t1 = get_t1(mse)
        lesion_new = make_lesion(mse)
        lesion_old = glob("{}/{}/sienaxorig_*/lesion_mask.nii.gz".format(_get_output(mse),mse))
        if len(lesion_old)>=1:
            les_old = lesion_old[0]
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")



            df.loc[idx, "diff"] = x

        df.loc[idx, "msid"] = msid
        """df.loc[idx, "t1 dimensions"] = check_dim(t1)
        df.loc[idx, "sienax dim"] = check_dim(sienax)
        df.loc[idx, "lesion dim"] = check_dim(lesion)
        df.loc[idx, "lesion origspace dim"] = check_dim(get_les_origspace(mse))
        df.loc[idx, "lst long dim"] = check_dim(get_lst_long(msid))"""


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