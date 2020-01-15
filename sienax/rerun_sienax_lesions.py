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
        if not os.path.exists(new_lesion) and os.path.exists(s):
            cmd = ["flirt", "-init", affine_inv, "-applyxfm", "-in", s, "-ref", get_t1(mse), "-o",new_lesion]
            print("flirt", "-init", affine_inv, "-applyxfm", "-in", s, "-ref", get_t1(mse), "-o",new_lesion)
            Popen(cmd).wait()
        #if not os.path.exists(new_lesion):
            #new_lesion = ""
    return new_lesion

def get_lesion(mse):
    sienax_flair_mni = "{}/{}/sienaxorig_flair/lesion_mask.nii.gz".format(_get_output(mse),mse)
    sienax_t2_mni = "{}/{}/sienaxorig_t2/lesion_mask.nii.gz".format(_get_output(mse),mse)
    lesion_orig =""
    t1 = get_t1(mse).split('/')[-1].replace(".nii.gz","")
    print(t1)
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

def check_errormap(les_orig, les_new):
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
    return [out, o]

def compare_dimensions(les_orig, les_new, t1):
    from nipype.algorithms.metrics import Similarity
    dim3_orig = dim3_new = dim3_t1 =""
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

    cmd = ["fslhd", t1]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    for line in output:
        if "dim3" in line:
            dim3_t1 = line


    print("DIMENSION COMPARISON", dim3_orig, dim3_new, dim3_t1)
    if dim3_orig == dim3_new == dim3_t1:
        dimension = "all dimensions are equal"
    elif dim3_orig == dim3_new:
        dimension = "only lesion dimensions are equal"
    elif not dim3_orig == dim3_new and dim3_orig == dim3_t1:
        dimension = "original lesion dimensions equal to T1 but not new"
    elif not dim3_orig == dim3_new and dim3_new == dim3_t1:
        dimension = "new lesion dimensions equal to T1 but not original"
    else:
        dimension = "no dimensions are equal"
    return dimension


def check_error(mse):

    error = sienax =dimension = out = o = overlap = les_overlap = ""
    les_orig = get_lesion(mse)
    les_new = make_lesion(mse)
    t1 = get_t1(mse)
    if len(les_orig)>0:
        sienax = les_orig.split('/')[6]

    if os.path.exists(les_orig) and os.path.exists(les_new) and os.path.exists(t1):
        error = "all files exist"
        check_dim(les_orig,error)
        l_orig = nib.load(les_orig)
        l_new = nib.load(les_orig)
        y = l_orig.header['dim'] # get_data()
        x = l_new.header['dim'] # get_data()

        if str(x) == str(y):  #.all():
            try:
                errormap = ErrorMap()
                errormap.inputs.in_ref = les_orig
                errormap.inputs.in_tst = les_new
                errormap.inputs.metric = 'euclidean'
                res = errormap.run()
                o = res.outputs.distance
                print(o)

                if not o == 0.0:
                    print(les_orig, les_new)
                    print("^^^^^^^^^^^^^^^^^^^^")
                    print(mse, o)
                    print("*********************")
                    error = "BAD LESION MASK 1"
                    #run_sienax_ongrid(mse)
                    #run_sienax(mse, les_new)
                    print(mse, "rerun sienax")
                else:
                    error = "BEAUTIFUL <3"
                    print(mse, "YAY GOOD")

                
            except:
                pass
                """dim3_orig = dim3_new = ""
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

                if not dim3_orig == dim3_new:
                    print("copying the geometry....")
                    cpgeom = CopyGeom(in_file=les_orig, dest_file=les_new)
                    print(les_orig, les_new)
                    cpgeom.run()
                    #print(cpgeom.runtime.stdout)
                    try:
                        errormap = ErrorMap()
                        errormap.inputs.in_ref = les_orig
                        errormap.inputs.in_tst = les_new
                        errormap.inputs.metric = 'sqeuclidean'
                        #errormap.inputs.mask = get_t1(mse)
                        res = errormap.run()
                        o = res.outputs.distance
                        print(o)
                        if not o == 0.0:
                            print(mse, "rerun sienax")
                            error = "BAD LESION MASK 2"
                            #run_sienax_ongrid(mse)
                            #run_sienax(mse, les_new)
                        else:
                            print(mse, "YAY GOOD")
                            error = "BEAUTIFUL <3"
                    except:
                        pass"""


    """else:
        if not os.path.exists(les_orig) :
            error = "original lesion missing"
            if os.path.exists("{}/{}/sienax_optibet/".format(_get_output(mse),mse,)):
                lesion = "{}/{}/sienax_optibet/{}/lesion_mask.nii.gz".format(_get_output(mse),mse, t1.split('/')[-1].replace(".nii.gz",""))
                error = "original lesion missing - sienax optibet run"
                if os.path.exists(lesion):
                    error = "original lesion missing - sienax optibet with LESION run"
        if not os.path.exists(les_new):
            error = "new lesion missing"
            if os.path.exists("{}/{}/sienax_optibet/".format(_get_output(mse),mse,)):
                lesion = "{}/{}/sienax_optibet/{}/lesion_mask.nii.gz".format(_get_output(mse),mse, t1.split('/')[-1].replace(".nii.gz",""))
                error = "new lesion missing - sienax optibet run"
                if os.path.exists(lesion):
                    error = "new lesion missing - sienax optibet with LESION run"
        if not os.path.exists(t1):
            error = "t1 missing"""""

    #error = "missing file"
    print(mse, error)
    return [error, sienax]


def overlap(t1):
    overlap = ""
    sienax_optibet = "{}/{}/sienax_optibet/{}/".format(_get_output(mse), mse, t1.split('/')[-1].replace(".nii.gz",""))
    I_brain = sienax_optibet + "I_brain_mask.nii.gz"
    optibet_les = sienax_optibet + "lesion_mask.nii.gz"
    out_test = "/data/henry6/gina/s_test/" + mse +".nii.gz"
    if os.path.exists(optibet_les):
        cmd = ["fslmaths", I_brain, "-ero", out_test.replace(".nii", "-ero.nii")]
        Popen(cmd).wait()

        cmd = ["fslmaths", out_test.replace(".nii", "-ero.nii"), "-add", optibet_les, "-bin", out_test]
        Popen(cmd).wait()
        if os.path.exists(out_test):

            overlap = Overlap()
            overlap.inputs.volume1 = out_test
            overlap.inputs.volume2 = I_brain
            overlap.inputs.bg_overlap = False
            overlap.inputs.vol_units = "mm"
            Over = overlap.run()
            o = Over.outputs.roi_voldiff[0]
            x = Over.outputs.jaccard
            print(o,x)
            if o > .01 or x < .9 or o < -0.01:
                print(mse, o, x)
                overlap = "bad"
    return overlap

def lesion_overlap(les_orig, les_new):
    les_overlap = ""
    out_test = "/data/henry6/gina/s_test/" + mse +".nii.gz"
    les_dil = out_test.replace(".nii.gz","_dilLES.nii.gz" )
    les_mul = out_test.replace(".nii.gz","_mulLES.nii.gz" )
    cmd = ["fslmaths", les_new, "-dilM",les_dil ]
    Popen(cmd).wait()

    cmd = ["fslmaths",les_dil,"-mul", les_orig,les_mul]
    Popen(cmd).wait()
    try:

        overlap = Overlap()
        overlap.inputs.volume1 = les_dil
        overlap.inputs.volume2 = les_mul
        overlap.inputs.bg_overlap = False
        overlap.inputs.vol_units = "mm"
        Over = overlap.run()
        o = Over.outputs.roi_voldiff[0]
        x = Over.outputs.jaccard
        print(o,x)
        if o > .01 or x < .9 or o < -0.01:
            print(mse, o, x)
            les_overlap = "bad"
    except:
        les_overlap = "lesions have different dimensions"
        pass
    return les_overlap


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
    """mse_list = ["mse4713", "mse4530", "mse4714", "mse5649", "mse4717", "mse4721", "mse4530", "mse3574", "mse1307"]
    for mse in mse_list:
        check_error(mse)"""


    for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx, 'mse']
        c = check_error(mse)
        les_orig = get_lesion(mse)
        les_new = make_lesion(mse)
        t1 = get_t1(mse)
        print("!!!!!!!!!!!!!!!!!", c[1])
        #error = check_errormap(les_orig, les_new)
        df.loc[idx, "lesion error"] = c[0]
        df.loc[idx, "sienax"] = c[1]
        #df.loc[idx, "dimensions"] = compare_dimensions(les_orig, les_new, t1)
        #df.loc[idx, "error"] = error[0]
        #df.loc[idx, "distance"] = error[1]
        print(overlap(t1), lesion_overlap(les_orig,les_new))
        #df.loc[idx, "overlap"] = overlap(t1)
        #df.loc[idx, "overlap les"] = lesion_overlap(les_orig, les_new)

    df.to_csv("{}".format(out))
