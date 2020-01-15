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


def reg_to_BL(mse_list, long):
    bl_mse = mse_list[0]
    bl_t1 = get_t1(bl_mse)
    other_mse = mse_list[1:]
    for mse in other_mse:
        t1_in = get_t1(mse)
        jacobian_path = "{}/{}/jacobian/".format(_get_output(mse), mse)
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

        if not os.path.exists(long +"/first/"):os.mkdir(long + "/first/")
        out_first = long +"/first/" + mse + "first.nii.gz"

        cmd = ["flirt","-init",affine, "-applyxfm", "-in", get_first(mse),"-ref", bl_t1, "-out", out_first]
        Popen(cmd).wait()

        cmd = ["fslmaths", out_first, "-bin", out_first.replace(".n","-bin.n")]
        Popen(cmd).wait()

        cmd = ["fslmaths", get_first(bl_mse),"-bin", long + '/first/'+ bl_mse+"first_seg-bin_BL"]
        Popen(cmd).wait()

        shutil.copy(get_first(bl_mse),long + '/first' + bl_mse + "-first_segBL.nii.gz" )


def combine_first(mse_long, long):
    combined_first_mask = long + "/first/combined-first_mask.nii.gz"
    #num = len([name for name in os.listdir(long) if "first_seg-bin" in name])
    first_list = []
    for first in os.listdir(long):
        if "first_seg-bin" in first:
            first_list.append(long +'/first/'+ first)
    print(first_list)


    combined_image = nilearn.masking.intersect_masks(first_list, threshold=0.5, connected=True)
    combined_image.to_filename(long + "combined_first-bin.nii.gz")
    cmd = ["fslmaths", get_first(mse_long[0]), "-dilM", "-mul", long+"/first/combined_first-bin.nii.gz", combined_first_mask]
    Popen(cmd)
    return combined_first_mask

def mult_jacobia(long, first_mask):
    for files in os.listdir(long):
        if "jacobian" in files:
            mse = files.split("_ja")[0]
            cmd = ["fslmaths", long + files, "-mul", first_mask, long +'/first/'+ mse+ "jacobia_first.nii.gz"]
            Popen(cmd).wait()


def get_first(mse):
    first = ""
    first_seg = glob("{}/{}/first_all/*first*seg*.nii.gz".format(_get_output(mse),mse))
    if len(first_seg) == 0:
        cmd = ["pbr", mse, "-w", "first_all", "-R"]
        Popen(cmd).wait()
    else:
        print(mse, "EXISTS")
        first = first_seg[0]
    return first


def get_mse(df):
    ms = "ms1753"
    mse_list = []
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx, "mse"]
        if msid == ms:
            mse_list.append(mse)
        else:
            ms = msid
            mse_list = []
        long = config["long_output_directory"] +"/"+msid + "/average_masks/"
        if not os.path.exists(config["long_output_directory"] +"/"+msid):
            os.mkdir(config["long_output_directory"] +"/"+msid)
        if not os.path.exists(long):
            os.mkdir(long)
        reg_to_BL(mse_list, long)

    return mse_list, long



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))
    dir = get_mse(df)
    first_mask = combine_first(dir[0], dir[1])
    mult_jacobia(dir[1], first_mask)





