from subprocess import check_call
import os
from glob import glob
import argparse
from pbr.config import config
import pandas as pd
from pbr.base import _get_output
from subprocess import Popen, PIPE
import json

df = pd.read_csv("/home/sf522915/Documents/COMPLETE_EPIC_dec11.csv")



def get_lesion_mask(pbr, t1):
    sienax_optibet_les = "{}/sienax_optibet/{}/lesion_mask.nii.gz".format(pbr, t1)
    lesion_orig_flair = "{}/sienaxorig_flair/lesion_mask.nii.gz".format(pbr)
    lesion_orig_t2 = "{}/sienaxorig_t2/lesion_mask.nii.gz".format(pbr)
    lesion_new = "{}/new_lesion/lesion.nii.gz".format(pbr)
    if os.path.exists(sienax_optibet_les):
        les = sienax_optibet_les
    elif os.path.exists(lesion_orig_flair):
        les = lesion_orig_flair
    elif os.path.exists(lesion_orig_t2):
        les = lesion_orig_t2
    elif os.path.exists(lesion_new):
        les = lesion_new
    else:
        les = ""
    return les


def get_t1(pbr):
    t1 = ""
    status = pbr + "/alignment/status.json"
    if os.path.exists(status):
        with open(status) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1_file = data["t1_files"][-1]
                t1 = t1_file.split('/')[-1].replace(".nii.gz","")

    return t1


def get_first(pbr, t1):
    first = ""
    first1 = "{}/first_all/{}_corrected_all_fast_firstsegs.nii.gz".format(pbr, t1)
    first2 ="{}/first_all/{}_all_fast_firstsegs.nii.gz".format(pbr, t1)
    if os.path.exists(first1):
        first = first1
    elif os.path.exists(first2):
        first = first2
    else:
        try:
            first = glob(pbr + "/first_all/*all_fast_firstseg*.nii.gz")[0]

        except:
            pass
    return first

def subtract_lesion(first, lesion_mask):
    les_bin = config["working_directory"] + mse + "lesion_bin.nii.gz"
    cmd = ["fslmaths", lesion_mask, "-bin", les_bin]
    print(cmd)
    Popen(cmd).wait()

    cmd = ["fslmaths", first, "-bin", "-sub", les_bin,"-mul",first, first.replace(".nii","_nolesion.nii")]
    print(cmd)
    Popen(cmd).wait()




for idx, row in df.iterrows():
    mse = str(row["mse"])
    print(mse)
    #if mse == "mse4530":
    pbr = "{}/{}/".format(_get_output(mse), mse)
    t1 = get_t1(pbr)
    first = get_first(pbr,t1)
    lesion_mask =get_lesion_mask(pbr, t1)
    if os.path.exists(first) and os.path.exists(lesion_mask) and not os.path.exists(first.replace(".nii","_nolesion.nii")):
        subtract_lesion(first, lesion_mask)

    if not os.path.exists(first):
        print("NO FIRST",mse)
        if os.path.exists( "{}/first_all/".format(pbr)):
            print(mse, "DIFF FIRST")
    elif not os.path.exists(lesion_mask):
        print("NO LESION MASK", mse)
    else:
        print("YAYYYYYYYYYY", mse)

