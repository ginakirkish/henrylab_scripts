from subprocess import check_call, Popen, PIPE
import argparse
import json
from pbr.base import _get_output
from glob import glob
import os
import shutil
import pandas as pd
import time
import subprocess

import multiprocessing as mp
print("Number of processors: ", mp.cpu_count())

pbsdir = '/data/henry2/arajesh/PBR_utils/automation/pbs/'

def submit(shell_cmd):

    if '/' in shell_cmd.split(' ')[0]:
        job_name = '{}_{}'.format(shell_cmd.split(' ')[0].split('/')[-1], time.time())
    else:
        job_name = '{}_{}'.format(shell_cmd.split(' ')[0], time.time())
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
    print(cmd)
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




def get_mse(df, o):
    ind = 0
    baseline_msid, mse_baseline, mse2, mse1= ["","","",""]
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx, "mse"]

        """msid = "ms" + msid.replace("ms", "").lstrip("0")
        mse1 = str(df.loc[idx,'mse1'])
        mse2 = str(df.loc[idx, 'mse2'])
        print(mse1, mse2)
        if mse1.startswith("mse") and mse2.startswith("mse"):
            print("python", "/data/henry6/gina/scripts/grid_submit.py", "'{} {} {} {} {} {} {} {}'".format("pbr",mse1, mse2, "-w", "siena_optibet", "-R", "-rps", "09Rosie1313!"))
            cmd = ["pbr",mse1, mse2, "-w", "siena_optibet"] #.format(mse1, mse2)]
            #Popen(cmd).wait()"""

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
            df.loc[idx, "mse1"] = mse1
            df.loc[idx, 'mse2'] = mse2

    df.to_csv('{}'.format(o))


    """shell_cmd = "pbr {} {} -w siena_optibet -R".format(mse1, mse2) #
        #Popen(shell_cmd).wait()
        print(shell_cmd)
        submit(shell_cmd)"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument('-o', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    o = args.o
    df = pd.read_csv("{}".format(c))
    get_mse(df, o)

