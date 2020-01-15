from glob import glob
import pandas as pd
import numpy as np
import csv
import os
from subprocess import Popen, PIPE, check_call
from pbr.base import _get_output
import json
import nibabel as nib
import argparse
pbr_long = "/data/henry4/siena_BM/"




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
        msid = "ms" + msid.replace("ms", "").lstrip("0")
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
            #get_siena(c, out)
            siena_bet = glob("/{0}/{1}/siena_fromBL_BET/{2}_{3}".format(pbr_long, msid, mse1, mse2))
            siena_optibet = glob("/{0}/{1}/siena_fromBL_optiBET/{2}_{3}".format(pbr_long, msid, mse1, mse2))
            siena_optibet_ANTs = glob('/{0}/{1}/siena_ANTsBM_fromBL/{2}_{3}'.format(pbr_long, msid, mse1, mse2))
            siena_optibet_nrigid = glob('/{0}/{1}/siena_NrigidBM_fromBL/{2}_{3}'.format(pbr_long, msid, mse1, mse2))
            siena_monstr = glob('/{0}/{1}/siena_MONSTR/{2}_{3}'.format(pbr_long, msid, mse1, mse2))
            all_siena = [siena_bet, siena_optibet, siena_optibet_ANTs, siena_optibet_nrigid, siena_monstr]
            #for siena_long in all_siena:
            """if len(siena_bet) > 0:
                cmd = ["fslview", siena_bet[0] + "/A_halfwayto_scA_brain.nii.gz"]
                print("fslview", siena_bet[0] + "/A_halfwayto_scA_brain.nii.gz")
                check_call(cmd)

                cmd = ["fslview", siena_bet[0] + "/B_halfwayto_scB_brain.nii.gz"]
                print("fslview", siena_bet[0] + "/B_halfwayto_scB_brain.nii.gz")
                check_call(cmd)
            if len(siena_optibet) > 0:
                cmd = ["fslview", siena_optibet[0] + "/A_halfwayto_scA_brain.nii.gz"]
                print("fslview", siena_optibet[0] + "/A_halfwayto_scA_brain.nii.gz")
                check_call(cmd)

                cmd = ["fslview", siena_optibet[0] + "/B_halfwayto_scB_brain.nii.gz"]
                print("fslview", siena_optibet[0] + "/B_halfwayto_scB_brain.nii.gz")
                check_call(cmd)
            if len(siena_optibet_ANTs) > 0:
                cmd = ["fslview", siena_optibet_ANTs[0] + "/A_halfwayto_scA_brain.nii.gz"]
                print("fslview", siena_optibet_ANTs[0] + "/A_halfwayto_scA_brain.nii.gz")
                check_call(cmd)

                cmd = ["fslview", siena_optibet_ANTs[0] + "/B_halfwayto_scB_brain.nii.gz"]
                print("fslview", siena_optibet_ANTs[0] + "/B_halfwayto_scB_brain.nii.gz")
                check_call(cmd)"""
            if len(siena_optibet_nrigid) > 0:
                cmd = ["fslview", siena_optibet_nrigid[0] + "/A_halfwayto_scA_brain.nii.gz"]
                print("fslview", siena_optibet_nrigid[0] + "/A_halfwayto_scA_brain.nii.gz")
                check_call(cmd)

                cmd = ["fslview", siena_optibet_nrigid[0] + "/B_halfwayto_scB_brain.nii.gz"]
                print("fslview", siena_optibet_nrigid[0] + "/B_halfwayto_scB_brain.nii.gz")
                check_call(cmd)
            """if len(siena_monstr) > 0:
                cmd = ["fslview", siena_monstr[0] + "/A_halfwayto_scA_brain.nii.gz"]
                print("fslview", siena_monstr[0] + "/A_halfwayto_scA_brain.nii.gz")
                check_call(cmd)

                cmd = ["fslview", siena_monstr[0] + "/B_halfwayto_scB_brain.nii.gz"]
                print("fslview", siena_monstr[0] + "/B_halfwayto_scB_brain.nii.gz")
                check_call(cmd)"""



