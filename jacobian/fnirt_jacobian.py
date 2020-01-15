
import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
import json
import pandas as pd
from pbr.config import config
import shutil
import nibabel as nib
import nilearn
from nilearn import masking



def get_t1(mse):
    t1 = ""
    align = "{}/{}/alignment/status.json".format(_get_output(mse), mse)
    if os.path.exists(align):
        with open(align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1 = data["t1_files"][-1]
    return t1


def reg_to_BL(mse_list, msid):
    bl_mse = mse_list[0]
    bl_t1 = get_t1(bl_mse)
    other_mse = mse_list[1:]
    for mse in other_mse:
        t1_in = get_t1(mse)
        #affine = t1_in.replace(".nii.gz", ".mat")
        jacobian_path = config["long_output_directory"] +"/"+msid + '/jacobian/'

        if not os.path.exists(jacobian_path):
            os.mkdir(jacobian_path)

        affine = jacobian_path + bl_mse + "_affinereg_" + mse + ".mat"
        affine_reg = jacobian_path + bl_mse + "_affinereg_" + mse + ".nii.gz"
        fnirt_reg = jacobian_path + bl_mse + "_fnirt_" + mse + ".nii.gz"
        jacobian = jacobian_path + bl_mse + "_jacobian_" + mse + ".nii.gz"
        cmd=['flirt','-ref',bl_t1,'-in',t1_in,'-omat',affine,'-out',affine_reg]
        Popen(cmd).wait()

        cmd=['fnirt','--ref='+bl_t1,'--in='+t1_in,'--aff='+affine,'--iout='+fnirt_reg,'--jout='+jacobian]
        Popen(cmd).wait()


def get_mse(df):
    ms = "ms1757"
    mse_list = []
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx, "mse"]
        if msid == ms:
            mse_list.append(mse)
        else:
            ms = msid
            mse_list = []
        reg_to_BL(mse_list,msid)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))
    dir = get_mse(df)