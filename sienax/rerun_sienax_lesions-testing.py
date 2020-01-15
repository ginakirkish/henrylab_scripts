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
import nibabel as nib
from nipype.algorithms.metrics import ErrorMap, Distance, Overlap, Similarity
import pandas as pd
from nipype.interfaces.fsl import CopyGeom
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
    lesion_mni = "{}/{}/lesion_mni/lesion_final_new.nii.gz".format(_get_output(mse),mse)
    affine = "{}/{}/alignment/mni_affine.mat".format(_get_output(mse), mse)
    affine_inv = affine.replace(".mat", "_inv.mat")
    if os.path.exists(sienax_flair_mni):
        s = sienax_flair_mni
    elif os.path.exists(sienax_t2_mni):
        s = sienax_t2_mni
    elif os.path.exists(lesion_mni):
        s = lesion_mni
    else:
        les_mni = glob("/data/henry*/working/{}/lesion_mni/lesion_final_new.nii.gz".format(mse))
        if len(les_mni)>0:
            s = lesion_mni[0]
        else:
            s = ""

    cmd = ["convert_xfm", "-omat",  affine_inv, "-inverse", affine]
    #print(cmd)
    Popen(cmd).wait()
    if os.path.exists(affine_inv):
        les_out = "{}/{}/new_lesion/".format(_get_output(mse), mse)
        if not os.path.exists(les_out):
            os.mkdir(les_out)
        new_lesion = les_out + "/lesion.nii.gz"
        #if not os.path.exists(new_lesion) and os.path.exists(s):
        cmd = ["flirt", "-init", affine_inv, "-applyxfm", "-in", s, "-ref", get_t1(mse), "-o",new_lesion]
        #print("flirt", "-init", affine_inv, "-applyxfm", "-in", s, "-ref", get_t1(mse), "-o",new_lesion)
        Popen(cmd).wait()
        #if not os.path.exists(new_lesion):
            #new_lesion = ""
    return new_lesion

def get_lesion(mse):
    sienax_flair_mni = "{}/{}/sienaxorig_flair/lesion_mask.nii.gz".format(_get_output(mse),mse)
    sienax_t2_mni = "{}/{}/sienaxorig_t2/lesion_mask.nii.gz".format(_get_output(mse),mse)
    lesion_orig =""
    t1 = get_t1(mse).split('/')[-1].replace(".nii.gz","")
    #print(t1)
    sienax_optibet = glob("{}/{}/sienax_optibet/ms*/lesion_mask.nii.gz".format(_get_output(mse),mse))
    if len(sienax_optibet) >0: #os.path.exists(sienax_optibet):
        lesion_orig = sienax_optibet[-1]
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




def run_sienax(mse, l_new):
    cmd = ["pbr", mse, "-w","sienax_optibet", "-R"]
    Popen(cmd).wait()

def check_dim(les_orig, error):
    if len(les_orig) >1:
        if os.path.exists(les_orig.replace("lesion_mask","I_brain")):
            I_brain = les_orig.replace("lesion_mask","I_brain")
            l = nib.load(les_orig)
            I = nib.load(I_brain)
            y = l.header['dim'] # get_data()
            #print(y)
            x = I.header['dim'] # get_data()
            #print(y, x)
            if not str(x) == str(y):
                error = "BAD LESION MASK - dimensions are off"
    return error

def check_error(mse):

    error = sienax =""

    les_orig = get_lesion(mse)
    les_new = make_lesion(mse)
    t1 = get_t1(mse)
    if len(les_orig)>0:
        sienax = les_orig.split('/')[6]
    print("$$$$$$$$$$$",sienax)
    print("ORIGINAL LESION", les_orig)
    print("NEW LESION", les_new)
    print("T1", t1)
    if os.path.exists(les_orig) and os.path.exists(les_new) and os.path.exists(t1):
        error = "all files exist"
        check_dim(les_orig,error)
        l_orig = nib.load(les_orig)
        l_new = nib.load(les_orig)

        y = l_orig.header['dim'] # get_data()
        x = l_new.header['dim'] # get_data()
        print(y, x)
        print(les_orig)
        print(les_new)

        if str(x) == str(y):  #.all():
            from nipype.algorithms.metrics import Similarity
            distance = Distance()
            distance.inputs.volume1 = les_orig
            distance.inputs.volume2 = les_new
            distance.inputs.method = 'eucl_max'
            sim = distance.run() 
            out = sim.outputs.distance
            print("^^^^^^^^^^^^^^^^^^",mse)
            print("DISTANCE", out)
            errormap = ErrorMap()
            errormap.inputs.in_ref = les_orig
            errormap.inputs.in_tst = les_new
            errormap.inputs.metric = 'euclidean'
            res = errormap.run()
            o = res.outputs.distance
            print("ERRORMAP",  o)
            print("*********************")
            dim3_orig = dim3_new = ""
            cmd = ["fslhd", les_orig]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            for line in output:
                if "dim3" in line:
                    dim3_orig = line
                    print(mse, "dim3", line)

            cmd = ["fslhd", les_new]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            for line in output:
                if "dim3" in line:
                    dim3_new = line
            print("DIMENSION COMPARISON", dim3_orig, dim3_new)

            if not dim3_orig == dim3_new:
                print("copying the geometry....")
                #cpgeom = CopyGeom(in_file=les_orig, dest_file=les_new)
                #print(les_orig, les_new)
                #cpgeom.run()

            """overlap = Overlap()
            overlap.inputs.volume1 = les_orig
            overlap.inputs.volume2 = les_new
            res = overlap.run() # doctest: +SKIP
            ovd = overlap.outputs.roi_voldiff
            oj = overlap.outputs.jaccard
            od = overlap.outputs.roi_ji
            oj = overlap.outputs.jaccard
            ovoldiff = overlap.outputs.volume_difference
            print("roi voldiff", ovd)
            print("jaccard", oj)
            print("dice", od)
            print("vol diff", ovoldiff)
            print("roi_ji")"""
        #except:
            #pass
            

          


if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    df = pd.read_csv("{}".format(c))
    mse_list = ["mse4713", "mse4530", "mse4714", "mse5649", "mse4717", "mse4721", "mse4530", "mse3574", "mse1307"]
    for mse in mse_list:
        check_error(mse)


    """for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx, 'mse']
        c = check_error(mse)
        df.loc[idx, "lesion error"] = c[0]
        df.loc[idx, "sienax"] = c[1]"""

    df.to_csv("{}".format(out))
