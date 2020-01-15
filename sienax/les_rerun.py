import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import subprocess
from subprocess import Popen, PIPE
from getpass import getpass
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
import pandas as pd
import shutil
import nibabel as nib
import numpy as np
import time


def get_t1(mse):
    t1 = ""
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    if os.path.exists(align):
        with open(align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1 = data["t1_files"][-1]
    return t1

def make_lesion(mse):
    les_out = "{}/{}/new_lesion/".format(_get_output(mse), mse)
    new_lesion = ""
    sienax_flair_mni = "{}/{}/sienax_flair/lesion_mask.nii.gz".format(_get_output(mse),mse)
    sienax_t2_mni = "{}/{}/sienax_t2/lesion_mask.nii.gz".format(_get_output(mse),mse)

    inv_affine = "{}/{}/alignment/mni_affine_inv.mat".format(_get_output(mse),mse)

    if os.path.exists(sienax_flair_mni):
        s = sienax_flair_mni
    elif os.path.exists(sienax_t2_mni):
        s = sienax_t2_mni
    else:
        s = ""
    if os.path.exists(inv_affine):
        les_out = "{}/{}/new_lesion/".format(_get_output(mse), mse)
        if not os.path.exists(les_out):
            os.mkdir(les_out)
        new_lesion = les_out + "/lesion.nii.gz"
        #if not os.path.exists(new_lesion):
        cmd = ["flirt", "-init", inv_affine, "-applyxfm", "-in", s, "-ref", get_t1(mse), "-o",new_lesion]
        print("flirt", "-init", inv_affine, "-applyxfm", "-in", s, "-ref", get_t1(mse), "-o",new_lesion)
        Popen(cmd).wait()
        if not os.path.exists(new_lesion):
            new_lesion = ""
    #print(new_lesion)
    return new_lesion

def get_lesion(mse):
    sienax_flair_mni = "{}/{}/sienaxorig_flair/lesion_mask.nii.gz".format(_get_output(mse),mse)
    sienax_t2_mni = "{}/{}/sienaxorig_t2/lesion_mask.nii.gz".format(_get_output(mse),mse)
    lesion_orig =""
    t1 = get_t1(mse).split('/')[-1].replace(".nii.gz","")
    #print(t1)
    sienax_optibet = "{}/{}/sienax_optibet/{}/lesion_mask.nii.gz".format(_get_output(mse),mse,t1)
    if os.path.exists(sienax_optibet):
        lesion_orig = sienax_optibet
    elif os.path.exists(sienax_flair_mni):
        lesion_orig = sienax_flair_mni
    elif os.path.exists(sienax_t2_mni):
        lesion_orig = sienax_t2_mni
    else:
        lesion_orig = ""
    return lesion_orig

def run_sienax_ongrid(mse):
    shell_cmd ="pbr {0} -w sienax_optibet -R".format(mse)
    print(shell_cmd)

    pbsdir = '/data/henry2/arajesh/PBR_utils/automation/pbs/'

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



hen = ["henry7","henry11"]
for h in hen:
    for mse in os.listdir("/data/"+ h+"/PBR/subjects/"):
        #try:
        if mse.startswith("mse") and os.path.exists("/data/"+ h+"/PBR/subjects/" + mse +"/alignment/status.json"):


            les = get_lesion(mse)
            if len(les) >1:
                if os.path.exists(les.replace("lesion_mask","I_brain")):
                    I_brain = les.replace("lesion_mask","I_brain")
                    l = nib.load(les)
                    I = nib.load(I_brain)
                    y = l.header['dim'] # get_data()
                    #print(y)
                    x = I.header['dim'] # get_data()
                    #print(y, x)
                    if not str(x) == str(y):
                        #print(mse)
                        #print(les)
                        cmd = ["pbr", mse, "-w", "nifti", "align", "-R"]
                        #print(cmd)
                        #Popen(cmd).wait()

                        #new_lesion = make_lesion(mse)

                        #new_les = nib.load(new_lesion)
                        #dim_les = new_les.header['dim']
                        #print(new_les, dim_les)
                        #print(x, I)
                        t1 = get_t1(mse)
                        if len(t1)>0:
                            t1_file = nib.load(t1)
                            dim_t1 = t1_file.header['dim']
                            #print(dim_t1, dim_les)
                            affine = "{}/{}/alignment/mni_affine.mat".format(_get_output(mse), mse)
                            affine_inv = affine.replace(".mat", "_inv.mat")

                            cmd = ["convert_xfm", "-omat",  affine_inv, "-inverse", affine]
                            #print(cmd)
                            Popen(cmd).wait()

                            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                            print("convert_xfm", "-omat",  affine_inv, "-inverse", affine)
                            make_lesion(mse)
                            print("pbr", mse, "-w", "sienax_optibet","-R")
                            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

                            #run_sienax_ongrid(mse)
                            cmd = ["pbr", mse, "-w", "sienax_optibet","-R"]
                            #Popen(cmd).wait()

        #except:
            #pass



            """run_sienax_ongrid(mse)
            cmd = ["pbr", mse, "-w", "sienax_optibet","-R"]
            #Popen(cmd).wait()


            if str(dim_t1) == str(dim_les):
                cmd = ["fslview", t1, new_lesion ]
                Popen(cmd).wait()
                #print(x, dim_les)
                print(mse, "YAYYYYYY FIXED")

                cmd = ["pbr", mse, "-w", "sienax_optibet","-R"]
                Popen(cmd).wait()"""



