import os
from glob import glob
from subprocess import Popen, PIPE
import json
from nipype.interfaces import fsl
from nipype.interfaces.fsl import RobustFOV, Reorient2Std
from nipype.interfaces.c3 import C3dAffineTool
import argparse
import shutil
from nipype.interfaces.fsl import BinaryMaths, UnaryMaths, ErodeImage, ImageStats, Threshold, DilateImage
import numpy as np
import math
import pbr
from pbr.base import _get_output

def get_series(mse):
    t1, t2, flair = "","",""
    align = "{}/{}/alignment/status.json".format(_get_output(mse), mse)
    if os.path.exists(align):
        with open(align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1 = data["t1_files"][-1]
            if len(data["flair_files"]) > 0:
                flair = data["flair_files"][-1]
            if len(data["t2_files"]) > 0:
                t2 = data["t2_files"][-1]
    return [t1, t2, flair]


def get_t2_les(mse):
    t2_les_path = glob("{}/{}/lesion_origspace*/lesion.nii.gz".format(_get_output(mse),mse))
    if len(t2_les_path)>0:
        t2_les = t2_les_path[0]
    else:
        t2_les = ""
    return t2_les

def get_wm(mse, base_dir):
    wm_path = glob("{}/sienax_optibet/ms*/I_stdmaskbrain_pve_2.nii.gz".format(base_dir))
    if len(wm_path)>0:
        wm = wm_path[0]
    else:
        wm = ""
    return wm

def bin_les(t1_les_dir, t2_les):
    cmd = ["fslmaths", t2_les, "-bin", t1_les_dir +"/t2_lesion.nii.gz"]
    Popen(cmd).wait()

def n4_corr(t1, base_dir, wm):
    n4_path = '{}/N4corr/'.format(base_dir)
    n4 = '{}'.format(n4_path+ t1.split('/')[-1])
    if not os.path.exists(n4_path):
        os.mkdir(n4_path)
    if not os.path.exists(n4):
        cmd = ["N4BiasFieldCorrection", "-d", "3", "-i", t1,"-w", wm, "-o",n4]
        Popen(cmd).wait()
    return n4

def get_wm_metrics(t1_les_dir, wm_eroded):
    cmd = ["fslstats", wm_eroded, "-P", "50"]
    proc = Popen(cmd, stdout=PIPE)
    median_nawm = float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0])
    new_median_nawm = median_nawm + .000001
    print("NEW MEDIAN", new_median_nawm)

    cmd = ["fslmaths",  wm_eroded, "-thr", str(new_median_nawm), t1_les_dir+"/ero_WM_Uhalf.nii.gz"]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    print(cmd)

    cmd = ["fslstats", t1_les_dir+ "/ero_WM_Uhalf.nii.gz", "-S"]
    proc = Popen(cmd, stdout=PIPE)
    std_nawm = float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0])
    print(std_nawm, "THIS IS THE STANDARD DEVIATION of NAWM")
    est_std = float(std_nawm) * 1.608

    cmd = ["fslstats", wm_eroded, "-V"]
    proc = Popen(cmd, stdout=PIPE)
    vol_nawm = float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0])
    print(vol_nawm, "THIS IS THE VOLUME OF THE NAWM")
    return [new_median_nawm, est_std, vol_nawm]


def get_les_metrics(t1_les_dir, les_mul_t1):
    cmd = ["fslstats", les_mul_t1, "-P", "50"]
    proc = Popen(cmd, stdout=PIPE)
    median_lesion =  float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0])
    print(median_lesion, "THIS IS THE LESION MEDIAN")
    new_median_lesion = median_lesion - .000001

    cmd = ["fslmaths",  les_mul_t1, "-uthr", str(new_median_lesion), t1_les_dir+ "/lesion_Lhalf.nii.gz"]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    print(cmd)

    cmd = ["fslstats",t1_les_dir +"/lesion_Lhalf.nii.gz" , "-S"]
    proc = Popen(cmd, stdout=PIPE)
    std_lesion = float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0])
    print(std_lesion, "THIS IS THE STANDARD DEVIATION for the lesion lower half")
    est_std = std_lesion * 1.608
    #echo 20.077990*1.608 | bc

    cmd = ["fslstats", les_mul_t1, "-V"]
    proc = Popen(cmd, stdout=PIPE)
    vol_lesion = float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0])
    print(vol_lesion, "THIS IS THE VOLUME OF THE lesion")
    return [new_median_lesion, est_std, vol_lesion]

def fill_les_hole(t1_les_dir, t2_les):
    cmd = ["fslmaths", t2_les, "-fillh",t1_les_dir + "/t2_les.nii.gz"]
    Popen(cmd).wait()
    t2_les = t1_les_dir + "/t2_les.nii.gz"
    return t2_les



def create_t1_les(mse, t1, t2_les, base_dir, wm):
    t1_les_dir = '{}/t1_les/'.format(base_dir)
    if not os.path.exists(t1_les_dir):
        os.mkdir(t1_les_dir)

    bin_les(t1_les_dir, t2_les)
    t1 = n4_corr(t1, base_dir, wm)

    wm_eroded = t1_les_dir + "/wm_eroded.nii.gz"
    wm_with_les = t1_les_dir+ "/wm_withles.nii.gz"
    wm_t1 = t1_les_dir + "/wm_t1.nii.gz"
    les_mul_t1 = t1_les_dir + "/t1_mul_les.nii.gz"
    prob_map = t1_les_dir +"/prob_map.nii.gz"

    t2_les = fill_les_hole(t1_les_dir, t2_les)

    cmd = ["fslmaths", wm,"-add",t2_les,"-fillh", "-bin", "-ero", "-thr", ".1", "-mul",t1, wm_eroded]
    print("fslmaths", wm,"-add",t2_les, "-fillh", "-bin", "-ero", "-thr", ".1", "-mul",t1, wm_eroded)
    Popen(cmd).wait()
    
    cmd = ["fslmaths", wm, "-bin", "-mul", t1, wm_t1]
    Popen(cmd).wait()
    
    cmd = ["fslmaths", t2_les, "-bin", "-mul", t1, les_mul_t1]
    Popen(cmd).wait()

    # calculating estimated median and standard deviation for nawm
    median_nawm = get_wm_metrics(t1_les_dir, wm_eroded)[0]
    std_nawm = get_wm_metrics(t1_les_dir, wm_eroded)[1]
    vol_nawm = get_wm_metrics(t1_les_dir, wm_eroded)[2]

    #calculate wm histogram
    std_times2 = std_nawm*std_nawm*2
    x = (math.sqrt(std_times2*(math.pi)))
    part1 = vol_nawm/(math.sqrt(std_times2*(math.pi)))
    cmd = ["fslmaths", wm_t1, "-sub",str(median_nawm),"-sqr", "-div", str(std_times2), "-mul", "-1", "-exp", "-mul", str(part1), t1_les_dir+"/wm_hist.nii.gz"]
    Popen(cmd).wait()
    
    # calculating estimated median and standard deviation for lesions
    median_lesion = get_les_metrics(t1_les_dir, les_mul_t1)[0]
    std_lesion = get_les_metrics(t1_les_dir, les_mul_t1)[1]
    vol_lesion = get_les_metrics(t1_les_dir, les_mul_t1)[2]

     # lesion histogram
    if not vol_lesion == 0.0:
        lesion_times2 = std_lesion*std_lesion*2
        part2 = vol_lesion/(math.sqrt(lesion_times2*(math.pi)))
        cmd = ["fslmaths", wm_t1, "-sub",str(median_lesion),"-sqr", "-div", str(lesion_times2), "-mul", "-1", "-exp", "-mul", str(part1),t1_les_dir+"/lesion_hist.nii.gz"]
        Popen(cmd).wait()

        final_lesion = t1_les_dir + "/lesion_final_new.nii.gz"

        # making the probability map
        cmd = ["fslmaths", t1_les_dir+"/lesion_hist.nii.gz", "-add", t1_les_dir+ "/wm_hist.nii.gz",t1_les_dir+"/add_his.nii.gz"]
        Popen(cmd).wait()

        cmd = ["fslmaths",t1_les_dir +"/lesion_hist.nii.gz", "-div",t1_les_dir+ "/add_his.nii.gz","-mul", wm, prob_map]
        Popen(cmd).wait()

        cmd = ["fslmaths", t2_les, "-dilM", t1_les_dir + "/les_dil.nii.gz"]
        Popen(cmd).wait()

        cmd = ["fslmaths", prob_map,"-mul",t1_les_dir +"/les_dil.nii.gz" , "-thr", ".9","-bin","-fillh", final_lesion]
        Popen(cmd).wait()


        """

        # eroding the wm mask, taking out some problematic structures
        cmd = ["fslmaths",wm_MNI, "-sub", no_wm, "-thr", ".1","-ero","-ero", "-bin", wm_no_bs]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]


        cmd = ["fslmaths", prob_map,"-mul", wm_no_bs, "-thr", ".99", "-bin", base_dir+ "/lesion_prob_map.nii.gz" ]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]

        cmd = ["fslmaths", gm_MNI, "-bin","-dilM", base_dir + "/gm_dil.nii.gz"]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]


        cmd = ["fslmaths",lesion_bin_MNI, "-dilM","-dilM","-dilM","-dilM", "-mul", wm_MNI, "-mul", prob_map, "-thr", ".99999","-bin", "-sub", base_dir + "/gm_dil.nii.gz", "-thr", ".1","-mul", wm_MNI, "-bin", final_lesion]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]


        cmd = ["fslmaths", prob_map, "-mul", lesion_bin_MNI, "-thr", ".99", "-add", final_lesion, "-bin","-mul", wm_eroded, "-bin", base_dir+ "/lesion_prob_map_t1.nii.gz"]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]


        cmd = ["fslview",wm_eroded, wm_with_les,prob_map, final_lesion, t1_file, base_dir+ "/lesion_prob_map_t1.nii.gz" ]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]


        cmd = ["sienax_optibet", t1_file, "-lm", base_dir+ "/lesion_prob_map_t1.nii.gz", "-r", "-d", "-o", PBR_base_dir + "/" + mseid + "/sienax_t1_les/"]
        print("Running SIENAX....", cmd)
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]"""




if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code gives you a T1 lesion mask give a T2 lesion mask - mse is the input')
    parser.add_argument('mse', nargs="+")
    args = parser.parse_args()
    mse = args.mse[0]
    print("mse is:", mse)
    base_dir = "{}/{}/".format(_get_output(mse),mse)
    t1 = get_series(mse)[0]
    t2 = get_series(mse)[1]
    flair = get_series(mse)[2]
    t2_les = get_t2_les(mse)
    wm = get_wm(mse, base_dir)
    print(t1, t2_les)
    create_t1_les(mse, t1, t2_les, base_dir, wm)

