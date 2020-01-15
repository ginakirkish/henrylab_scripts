
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
import subprocess
import time

def get_t1(mse):
    t1 = ""
    align = "{}/{}/alignment/status.json".format(_get_output(mse), mse)
    if os.path.exists(align):
        with open(align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1 = data["t1_files"][-1]
                t1 = t1.replace("N4corr", "").replace("reorient", "").replace("brain_mask", "")
    return t1

pbsdir = '/data/henry2/arajesh/PBR_utils/automation/pbs/'

def run_grid(shell_cmd):
    #shell_cmd = "'{}'".format(shell_cmd)
    if '/' in shell_cmd.split(' ')[0]:
        job_name = '{}_{}'.format(shell_cmd.split(' ')[0].split('/')[-1], time.time())
    else:
        job_name = '{}_{}'.format(shell_cmd.split(' ')[0], time.time())
    #job_name = '{}_{}'.format('fnirt', time.time())
    job_name = job_name.replace("'","")
    print('job name', job_name)
    scriptfile = os.path.join(pbsdir, job_name+'.sh')

    fid = open(scriptfile,"w")
    fid.write("\n".join(["#! /bin/bash",
                         "#$ -V",
                         "#$ -q ms.q",
                         "#$ -l arch=lx24-amd64",
                         "#$ -v MKL_NUM_THREADS=1",
                         "#$ -l h_stack=32M",
                         "#$ -l h_vmem=5G",
                         "#$ -N {}".format(job_name),
                         "\n"]))

    fid.write("\n".join(["hostname",
                         "\n"]))


    #PIPEs the error and output to specific files in the log directory
    fid.write(shell_cmd)
    fid.close()

    # Write the qsub command line
    qsub = ["cd",pbsdir,";","/netopt/sge_n1ge6/bin/lx24-amd64/qsub", scriptfile]
    cmd = " ".join(qsub)
    print('%%%%%%%%%%%%%%%', cmd)
    # Submit the job
    print("Submitting job {} to grid".format(job_name))
    proc = subprocess.Popen(cmd,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE,
                            env=os.environ,
                            shell=True,
                            cwd=pbsdir)
    stdout, stderr = proc.communicate()
    print(stdout, stderr)



def reg_to_BL(mse_bl, mse, jacobian_dir, reg_to_bl):

    t1_in = get_t1(mse)
    bl_t1 = get_t1(mse_bl)
    if not os.path.exists(jacobian_dir):os.mkdir(jacobian_dir)
    if not os.path.exists(reg_to_bl):os.mkdir(reg_to_bl)

    affine = reg_to_bl + mse + "_affinereg_" + mse_bl + ".mat"
    affine_reg = reg_to_bl + mse + "_affinereg_" + mse_bl + ".nii.gz"
    fnirt_reg = reg_to_bl + mse + "_fnirt_" + mse_bl + ".nii.gz"
    jacobian = reg_to_bl + mse + "_jacobian_" + mse_bl + ".nii.gz"

    if not os.path.exists(affine_reg):
        cmd=['flirt','-ref',bl_t1,'-in',t1_in,'-omat',affine,'-out',affine_reg]
        Popen(cmd).wait()
    if not os.path.exists(fnirt_reg):
        #cmd=["python", "/data/henry6/gina/scripts/grid_submit.py", "{}".format('"fnirt'),'--ref='+bl_t1,'--in='+t1_in,'--aff='+affine,'--iout='+fnirt_reg,"{}{}".format('--jout='+jacobian,'"')]
        #print(cmd)
        #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        shell_cmd ="fnirt --ref={} --in={} --aff={} --iout={} --jout={}".format(bl_t1,t1_in, affine,fnirt_reg,jacobian)
        run_grid(shell_cmd)
        #cmd = ["python", "/data/henry6/gina/scripts/grid_submit.py", "'",'"', "{}".format('fnirt'),'--ref='+bl_t1,'--in='+t1_in,'--aff='+affine,'--iout='+fnirt_reg,'--jout='+jacobian, '"']
        #Popen(cmd).wait()




def run_all(msid, mse_list):
    long_dir = config["long_output_directory"] +"/"+msid
    jacobian_dir = long_dir +'/jacobian/'
    reg_to_bl = jacobian_dir + "/reg_to_bl/"
    if not os.path.exists(long_dir):os.mkdir(long_dir)
    mse_bl = mse_list[0]
    other_mse = mse_list[1:]
    for mse in other_mse:
        print(msid, mse_bl, mse)
        reg_to_BL(mse_bl, mse, jacobian_dir, reg_to_bl)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))
    ms = "ms1048"
    mse_list = []
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx, "mse"]
        if msid == ms:
            mse_list.append(mse)
        else:
            print(mse_list, msid)
            run_all(msid, mse_list)
            ms = msid
            mse_list = []





"""if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))

    ms_bl_first = df['msid'].iloc[0]
    mse_list = []
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx, "mse"]
        mse_bl = df.loc[idx, "mse_bl"]
        if msid == ms_bl_first:
            mse_list.append(mse)
            #print(msid, mse_bl, mse, mse_list)
            #print("XXXXXXXXXXXXX")
        else:
            print(ms_bl_first, mse_list)

            run_all(ms_bl_first, mse_list)
            ms_bl_first = msid
            mse_list = []
            mse_list.append(mse)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = str(df.loc[idx, "mse"])
        mse_bl = str(df.loc[idx, "mse1"])
        if mse_bl.startswith("mse"):
            run_all(msid, mse_bl, mse)"""