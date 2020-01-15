from subprocess import check_call
from time import time
import argparse
import json
import pbr
from pbr.base import _get_output
from glob import glob
import os
import shutil
import pandas as pd

from itertools import repeat

#nrigid_path = "/data/henry6/gina/henrylab_utils/nrigid/"
pbr_long = "/data/henry10/PBR_long/subjects/"

# working directory for registrations
wd = '/data/henry2/arajesh/py_scripts/notebooks/nrigid_dir/'



def get_t1(mse):
    with open('{0}/{1}/alignment/status.json'.format(_get_output(mse), mse)) as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1]
            print(t1_file)
        return t1_file

def get_bm(mse):
    BM = glob('{0}/{1}/sienaxorig_*/*/I_brain_mask.nii.gz'.format(_get_output(mse), mse))
    if BM:
        bm = BM[0]
    else:
        bm = ""
    return bm

def make_wd(mse1, mse2):
    msid = get_t1(mse1).split('/')[-1].split('-')[0]
    w_ants = pbr_long + msid + '/ants_BM/'
    wd = '{0}/{1}_{2}/'.format(w_ants, mse1, mse2)
    print("MSID:", msid)
    if not os.path.exists(w_ants):
        print(w_ants)
        os.mkdir(w_ants)

    if not os.path.exists(wd):
         print(wd)
         os.mkdir(wd)
    return wd



def run_ants(mse1, mse2, wd):
    print("THis is the fixed T1 image", get_t1(mse2))
    print("This is the moving T1 image", get_t1(mse1))
    print("This is the fixed brain mask", get_bm(mse2))
    print("This is the moving brain mask", get_bm(mse1))
    fixed = get_t1(mse2)
    moving = get_t1(mse1)
    output = wd + mse1 + "_" + mse2 + "space"
    output_bm = wd + mse1 + "_" + mse2 + "space_BM.nii.gz"
    output_matrix = output + "0GenericAffine.mat"
    msid = get_t1(mse1).split('/')[-1].split('-')[0]
    mse1_BM_final = wd + mse1 + '_mulBM_'+ mse2 + ".nii.gz"
    out_mat_inv = output + "1InverseWarp.nii.gz"
    mse2_BM_final = wd + mse2 + "_BM_final.nii.gz"
    siena_final = pbr_long + msid  + "/siena_ANTsBM_fromBL/"

    try:
        cmd = ["/data/henry7/software/ANTs/Scripts/antsRegistrationSyNQuick.sh","-t","sr", "-d", "3", "-f", fixed, "-m", moving, "-o", output]
        print("/data/henry7/software/ANTs/Scripts/antsRegistrationSyNQuick.sh","-d", "3", "-f", fixed, "-m", moving, "-o", output)
        check_call(cmd)
    except:
        print("FIRST FAILED")
        pass

    try:
        cmd = ["antsApplyTransforms", "-i", get_bm(mse1), "-r", get_t1(mse2), "-o", output_bm, "-t", output_matrix]
        print("antsApplyTransforms", "-i", get_bm(mse1), "-r", get_t1(mse2), "-o", output_bm, "-t", output_matrix)
        check_call(cmd)
    except:
        print("SECOND FAILED")
        pass
    try:
        cmd = ["fslmaths", output_bm, "-mul", get_bm(mse2), mse1_BM_final ]
        print(cmd)
        check_call(cmd)
    except:
        print("THIRD FAILED")
        pass
    try:
        cmd = ["antsApplyTransforms", "-d", "3", "-i", mse1_BM_final+".nii.gz", "-r", get_t1(mse1), "-t","["+output_matrix +",1]","-t", "["+out_mat_inv+"]", "-o", mse2_BM_final]
        print(cmd)
        check_call(cmd)
    except:
        print("FOURTH FAILEY")
        pass


    if not os.path.exists(siena_final):
        os.mkdir(siena_final)
    if not os.path.exists(siena_final + mse1+"_"+mse2):
        os.mkdir(siena_final + mse1+"_"+mse2)

    print("************************************************************")
    cmd =["/data/henry6/gina/scripts/siena_BMinput",get_t1(mse1), get_t1(mse2), "-bm1", mse2_BM_final,"-bm1", mse1_BM_final+".nii.gz", "-o", siena_final + mse1 + "_" +mse2 ]
    print("*************************************************************")
    print(cmd)
    check_call(cmd)



def run_all(mse1,mse2, wd):
    run_ants(mse1, mse2, wd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    """
    parser.add_argument('-mse1', help = 'MSE1 - Moving subject')
    parser.add_argument('-mse2', help = 'MSE2 - Reference Subject')
    args = parser.parse_args()
    mse1 = args.mse1
    mse2 = args.mse2
    wd = make_wd(mse1, mse2)
    mse1_t1 = get_t1(mse1)
    mse2_t1 = get_t1(mse2)
    print(wd)
    run_all(mse1, mse2, wd)
    """
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))
    ind = 0
    baseline_msid, mse_baseline, mse2 = ["","",""]
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
            print(mse1, mse)
            wd = make_wd(mse1, mse2)

            print("working directory", wd, mse1, mse2)
            run_all(mse1, mse2, wd)



