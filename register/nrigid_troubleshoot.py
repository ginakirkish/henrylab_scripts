from glob import glob
import pandas as pd
import numpy as np
import csv
import os
from subprocess import Popen, PIPE
from pbr.base import _get_output
import json
import nibabel as nib
import argparse
import nilearn
from nilearn import image

import shutil
#from PIL import Image, ImageOps


def get_t1(mse):
    with open('{0}/{1}/alignment/status.json'.format(_get_output(mse), mse)) as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1]
            print(t1_file)
        return t1_file


def get_hdr(t1_mse2):
    cmd = ["fslhd", t1_mse2]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    dim1, dim2, dim3 = "0", "0", "0"
    for items in output[5:6]:
        print(items[0], items[1])
        dim1 = items[1]
    for items in output[6:7]:
        print(items[0], items[1])
        dim2 = items[1]
    for items in output[7:8]:
        print(items[0], items[1])
        dim3 = items[1]
    total_dim = {"x": int(dim1), "y": int(dim2), "z": int(dim3)}
    print("DIMENSIONS:", total_dim)
    return total_dim


        #df.loc[idx, items[0]] = items[1]
    #dim1 = output.split("dim1")[0]
    #print(dim1)
    #output = output[0]
    #hd = float(output[0])
    #print(output)

def get_volume(mse_BM):
    cmd = ["fslstats", mse_BM, "-V"]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    output = output[0]
    volume = float(output[0])
    #print(volume)

    return volume

def make_pad(size_mse1, size_mse2):
    mse1_x = size_mse1["x"]
    mse2_y = size_mse2["y"]
    mse1_z = size_mse1["z"]
    mse2_x = size_mse2["x"]
    mse1_y = size_mse1["y"]
    mse2_z = size_mse2["y"]
    new_y, new_x, new_z = 0,0,0
    print(mse1_x, mse1_y, mse1_z)
    if mse1_x == mse2_x and mse1_y == mse2_y:
        print(mse1_x, mse2_x, "SAME SIZE")
        print(mse1_y, mse2_y, "SAME SIZE")
    elif mse1_x > mse2_x and mse1_y > mse2_y:
        new_x = mse1_x - mse2_x
        new_y = mse1_y - mse2_y
        new_z = mse1_z - mse2_z
        print(new_x, "x", new_y, "y")
        affine = np.diag(new_x, new_y)
        #shutil.copyfile(t1_mse1, t1_mse1.replace(".nii", "_padd.nii"))
        #nilearn.image.resample_image(t1_mse1.replace(".nii", "_padd.nii"), affine, target_shape=None)
    """if mse1_y == mse2_y:
        print(mse1_y, mse2_y, "SAME SIZE")
    elif mse1_y > mse2_y:
        new_y = mse1_y - mse2_y
        print(new_y, "y")
    if mse1_z == mse2_z:
        print(mse1_z, mse2_z, "SAME SIZE")
    elif mse1_z > mse2_z:
        new_z = mse1_z - mse2_z
        print(new_z, "z")"""




if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab siena values given a csv (with mse and msid) and an output csv')
    parser.add_argument('-i', help = 'csv containing the msid and mse')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    ind = 0
    baseline_msid, mse_baseline, mse2 = ["","",""]
    df = pd.read_csv('{0}'.format(c))
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx,'mse']

        if msid == baseline_msid:
            x = 0
            ind = ind+1
            #print(ind, msid, mse)
        else:
            baseline_msid = msid
            ind = 0
        if ind == 0 :
            mse1 =  df.loc[idx,'mse']
        if not mse1 == mse:
            mse2 = mse
            print(msid, mse1, mse2)
            df.loc[idx, "mse1"] = mse1
            df.loc[idx, "mse2"] = mse2
            t1_mse1 = get_t1(mse1)
            t1_mse2 = get_t1(mse2)
            df.loc[idx, "T1 mse1"] = t1_mse1
            df.loc[idx, "T1 mse2"] = t1_mse2
            size_mse1 = get_hdr(t1_mse1)
            size_mse2 = get_hdr(t1_mse2)
            try:
                make_pad(size_mse1, size_mse2)
            except:
                pass



            """
            nrigid= ""
            try:
                nrigid = glob('/data/henry6/gina/nrigid_test2/{0}/nrigid_test2/{1}_{2}/'.format(msid,mse1, mse2))[0]
                print(nrigid)

            except:
                pass
            if len(nrigid) > 0:
                mse1_BM = nrigid + "BM_{}.nii.gz".format(mse1)
                mse2_BM =nrigid + "BM_{}.nii.gz".format(mse2)
                if os.path.exists(mse1_BM):
                    print(mse1_BM)
                    vol_mse1 = get_volume(mse1_BM)
                    df.loc[idx, "mse1 BM V"] = vol_mse1
                    df.loc[idx, "mse1 BM"] = mse1_BM
                if os.path.exists(mse2_BM):
                    print(mse2_BM)
                    vol_mse2 = get_volume(mse2_BM)
                    df.loc[idx, "mse2 BM V"] = vol_mse2
                    df.loc[idx, "mse2 BM"] = mse2_BM
                df.to_csv("{}".format(out))"""
