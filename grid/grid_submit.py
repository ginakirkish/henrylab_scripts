#!/usr/bin/python

import os 
import pandas as pd
from pbr.base import _get_output
import subprocess
from glob import glob
import time
import argparse

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

def main(args):
    #print('The command you are running is', args.command)
    submit(args.command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('This script allows you to submit jobs via the grid -- you can type any command u want LOL')
    parser.add_argument('command', help='Type the command you want to run via the grid... for instance: "antsRegistration -m /data/henry10/in.nii.gz -f /data/henry10/ref.nii.gz -o nonlinear" |OR| "flirt -in /data/henry10/in.nii.gz -ref /data/henry10/ref.nii.gz -omat /data/henry10/flirt.mat **NOTE** You have to submit the absolute path"')
    args = parser.parse_args()
    #args = "{}{}{}".format('"',args, '"')
    main(args)
