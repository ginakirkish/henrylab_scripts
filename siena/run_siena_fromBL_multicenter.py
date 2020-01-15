
from subprocess import check_call, Popen
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

#pbr_long = "/data/henry10/PBR_long/subjects/"
pbr_long = "/data/henry12/siena_BM/"

def get_t1(mse):
    with open('{0}/{1}/alignment/status.json'.format(_get_output(mse), mse)) as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1]
            #print(t1_file)
            if not os.path.exists(t1_file.replace(".nii", "_N4corr.nii")):
                cmd = ["N4BiasFieldCorrection", "-d", "3", "-i", t1_file,"-o", t1_file.replace(".nii", "_N4corr.nii") ]
                check_call(cmd)
            t1_file = t1_file.replace(".nii", "_N4corr.nii")
        return t1_file


def make_wd(mse1, mse2):
    msid = get_t1(mse1).split('/')[-1].split('-')[0]
    w_bet = pbr_long + msid + '/siena_fromBL_BET/'
    wd = '{0}/{1}_{2}/'.format(w_ants, mse1, mse2)
    if not os.path.exists(w_bet):
        #print(w_ants)
        os.mkdir(w_bet)

    if not os.path.exists(wd):
         #print(wd)
         os.mkdir(wd)
    return wd



def run_siena(mse1, mse2, wd):
    #print("THis is the fixed T1 image", get_t1(mse2))
    #print("This is the moving T1 image", get_t1(mse1))

    wd_bet = pbr_long + msid + '/siena_fromBL_BET/{0}_{1}'.format(mse1, mse2)
    #print("************************************************************")


    if not os.path.exists(wd_bet + "/report.siena"):
        if not os.path.exists(wd_bet + "report.siena"):
            cmd =["siena",get_t1(mse1), get_t1(mse2),"-o", wd_bet]
            print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{0} {1} {2} {3} {4}"'.format("siena",get_t1(mse1), get_t1(mse2),"-o", wd_bet ))
    #print("*************************************************************")
    #print("siena",get_t1(mse1), get_t1(mse2),"-o", wd)
        #check_call(cmd)





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
            #print(mse1, mse)
            w_ants = pbr_long + msid + '/siena_fromBL_BET/'
            wd = '{0}/{1}_{2}/'.format(w_ants, mse1, mse2)
            #print(wd)
            #if not os.path.exists(wd + 'report.siena'):
            wd = make_wd(mse1, mse2)

            #print("working directory", wd, mse1, mse2)
            run_siena(mse1, mse2, wd)
