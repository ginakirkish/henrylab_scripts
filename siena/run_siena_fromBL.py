from subprocess import check_call, Popen, PIPE
import argparse
import json
from pbr.base import _get_output
from glob import glob
import os
import shutil
import pandas as pd

pbr_long = "/data/henry12/PBR_long/subjects_new/"

def n4_corr(t1_file,mse):
    try:
        N4corr = "{}/{}/N4corr/".format(_get_output(mse),mse)
        t1_n4 = N4corr + t1_file.split('/')[-1]
        if not os.path.exists(N4corr):
            os.mkdir(N4corr)
        if not os.path.exists(t1_n4):

            cmd = ["N4BiasFieldCorrection", "-d", "3", "-i", t1_file,"-o", t1_n4 ]
            print(cmd)
            check_call(cmd)
        return t1_n4
    except:
        pass


def check_for_resampling_sienax(t1_file):
    check = ""
    try:
        cmd = ["fslstats", t1_file, "-R" ]
        proc = Popen(cmd, stdout=PIPE)
        max = str(float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][-1]))
        check = ""
        if max.endswith(".0"):
            check = True
            print(check)
        else:
            check = False
    except:
        pass
    return check

def run_align(mse):
    cmd = ["pbr", mse, "-w", "nifti", "align", "-R"]
    Popen(cmd).wait()
    print(cmd)


def get_t1(mse):
    t1_file =""
    align = '{0}/{1}/alignment/status.json'.format(_get_output(mse), mse)
    #print(align)
    if os.path.exists(align):
        with open(align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1_file = data["t1_files"][-1]
                #print(t1_file)
            else:
                t1 = ""
    return t1_file



def run_siena(t1_mse1, t1_mse2, wd):
    print(t1_mse1, "^^^^^^^^^^^^")
    print(t1_mse2, "***********")
    cmd =["siena_optibet", t1_mse1, t1_mse2,"-o", wd]
    if not os.path.exists(wd + '/report.siena'):
        if os.path.exists(t1_mse2) and os.path.exists(t1_mse1):
            #cmd = ["siena_optibet", t1_mse1, t1_mse2, "-o", wd]
            #Popen(cmd).wait()
            print("siena_optibet", t1_mse1, t1_mse2, "-o", wd)
            #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{0} {1} {2} {3} {4}"'.format("siena_optibet", t1_mse1, t1_mse2,"-o", wd))


def make_wd(msid, mse1,mse2):
    w_msid = pbr_long + msid
    w_siena = w_msid + '/siena_optibet/'
    wd = '{0}/{1}_{2}/'.format(w_siena, mse1, mse2)
    if not os.path.exists(w_msid):
        os.mkdir(w_msid)
    if not os.path.exists(w_siena):
        os.mkdir(w_siena)
    #print("working directory", wd, mse1, mse2)
    return wd



def run_all(msid, mse1, mse2):
    wd = make_wd(msid, mse1, mse2)
    t1_mse1  = get_t1(mse1)
    t1_mse2 =  get_t1(mse2)

    #check1 = check_for_resampling_sienax(t1_mse1)
    #check2 = check_for_resampling_sienax(t1_mse2)
    #if check1 == True and check2 == True:
    try:
        t1_mse1 = n4_corr(t1_mse1, mse1)
        t1_mse2 = n4_corr(t1_mse2, mse2)
        #print(t1_mse1, t1_mse2, "these paths exist")
        if os.path.exists(t1_mse1):
            if os.path.exists(t1_mse2):
                run_siena(t1_mse1,t1_mse2, wd)
    except:
        pass
    #elif check1 == False:
        #run_align(mse1)
    #else:
        #run_align(mse2)


"""def get_mse(df):
    ind = 0
    baseline_msid, mse_baseline, mse2 = ["","",""]
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        msid = "ms" + msid.replace("ms", "").lstrip("0")
        mse = df.loc[idx,'mse']
        if msid == baseline_msid:
            x = 0
            ind = ind+1
        else:
            baseline_msid = msid
            ind = 0
        if ind == 0 :
            mse1 =  df.loc[idx,'mse']
        if not mse1 == mse:
            mse2 = mse
            run_all(msid, mse1, mse2)"""

def get_mse(df):
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        msid = "ms" + msid.replace("ms", "").lstrip("0")
        mse1 = df.loc[idx,'mse1']
        mse2 = df.loc[idx, "mse2"]
        run_all(msid, mse1, mse2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))
    get_mse(df)


