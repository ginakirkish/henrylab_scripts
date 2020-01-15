import numpy as np
import os
import pandas as pd
import subprocess
from subprocess import Popen, PIPE
from glob import glob
import time

import pbr
from pbr.base import _get_output

df = pd.read_csv("/home/sf522915/Documents/run_siena.csv")
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






def run_siena(msid, mse1, mse2):
    shell_cmd ="pbr {} {} -w siena_optibet -R".format(mse1, mse2)
    run_grid(shell_cmd)


    """try:
        siena = glob(str("/data/henry10/PBR_long/subjects/{0}/siena_optibet/*{1}*{2}*".format(msid,tp1_mse, tp2_mse)))[0]
        print(siena)
    except:

        cmd = "pbr" +" " + mse1 + " " + mse2 +" " + "-w" +" " + "siena_optibet" +" " + "-R"
            cmd = '"' + cmd +
            cmd = ["python", "/data/henry6/gina/scripts/grid_submit.py", cmd]
            print("running.....", cmd)
        cmd = ["pbr", mse1, mse2, "-w", "siena_optibet", "-R"]
        proc = Popen(cmd)
        proc.wait()

        pass"""

def run_align(mse):
    if not mse.endswith("nan"): #mse.startswith("mse"):
        if not os.path.exists(_get_output(mse) + '/' + mse):
            #cmd = "pbr" +" " + mse + " " + "-w" +" " +" " + "nifti" + " " + "align" +" " + "-R"
            #print(cmd)
            #cmd = ["python", "/data/henry6/gina/scripts/grid_submit.py", cmd]
            #print("running.....", cmd)
            cmd = ["pbr", mse, "-w", "nifti", "align", "-R"]
            proc = Popen(cmd)
            proc.wait()


for _, row in df.iterrows():
    msid = str(row["msid"])
    mse1 = row['mse_bl']
    mse2 = row['mse']

    siena_long = "/data/henry10/PBR_long/subjects/" + msid

    run_siena(msid, mse1, mse2)


