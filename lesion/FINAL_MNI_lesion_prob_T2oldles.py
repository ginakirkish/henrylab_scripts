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
from nipype.interfaces.base import CommandLine, CommandLineInputSpec, SEMLikeCommandLine, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import pandas as pd
import pbr
from pbr.base import _get_output




PBR_base_dir = '/data/henry10/PBR_long/subjects/'
no_wm = "/data/henry6/PBR/surfaces/MNI152_T1_1mm/mri/no_wm_MNI_new.nii.gz"

class imageData():
    def __init__(self, lesion_MNI, wm_MNI, t1_file, gm_MNI, t2_file):
        self.lesion_MNI = lesion_MNI
        self.wm_MNI = wm_MNI
        self.gm_MNI = gm_MNI

        self.t1_file = t1_file
        self.t2_file = t2_file


def find_lesion_MNI(mseid):

    if not os.path.exists(_get_output(mseid)+"/"+mseid+"/alignment/status.json"):
        run_pbr_align(mseid)

    with open(_get_output(mseid)+"/"+mseid+"/alignment/status.json") as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) == 0:
            #print("no {0} t1 files".format(tp))
            run_pbr_align(mseid)
            t1_file = "none"
        else:
            t1_file = data["t1_files"][-1]


        if len(data["t2_files"]) == 0:
            t2_file = "none"
        else:
            t2_file = data["t2_files"][-1]
            t2_file = format_to_baseline_mni(t2_file, "_T1mni.nii.gz")
            print(t2_file)


    lesion_MNI = str(glob(PBR_base_dir +  msid +  "/lesion_*.nii.gz"))[0]
    mni_long = PBR_base_dir + msid + "/MNI/"
    wm_MNI =  str(glob(PBR_base_dir + msid +  "/gm_*.nii.gz"))[0]
    gm_MNI = str(glob(PBR_base_dir +  msid +  "wm_*.nii.gz"))[0]

    if os.path.exists(wm_MNI):
        print(wm_MNI)
        if not os.path.exists(mni_long):
            os.mkdir(mni_long)

        print(wm_MNI,mni_long + "/wm_"+mseid + ".nii.gz")

    if os.path.exists(gm_MNI):
        if not os.path.exists(mni_long):
            os.mkdir(mni_long)
        print(gm_MNI)
        cmd = ["fslmaths", gm_MNI, "-bin", gm_MNI]
        proc = Popen(cmd)
        proc.wait()

        shutil.copyfile(gm_MNI,mni_long + "/gm_"+mseid + ".nii.gz")
        print(gm_MNI,mni_long + "/gm_"+mseid + ".nii.gz")


    if os.path.exists(lesion_MNI):
        print(lesion_MNI)

        if not os.path.exists(mni_long):
             os.mkdir(mni_long)
             print(mni_long)
        if not os.path.exists(mni_long+ "/lesion_"+mseid + ".nii.gz"):
            shutil.copyfile(lesion_MNI,mni_long + "/lesion_"+mseid + ".nii.gz")
            print(lesion_MNI,mni_long + "/lesion_"+mseid + ".nii.gz")

    return imageData(lesion_MNI, wm_MNI,  t1_file, gm_MNI, t2_file)
    print("FINISHED COPYING OVER MNI FILES....")



def run_pbr_align(mseid):

    alignment_folder = "/data/henry7/PBR/subjects/{0}/alignment".format(mseid)
    if os.path.exists(alignment_folder):
        cmd_rm = ['rm','-r', alignment_folder]
        print (cmd_rm)
        proc = Popen(cmd_rm)
        proc.wait()

    cmd = ['pbr', mseid, '-w', 'align', '-R']
    print (cmd)
    proc = Popen(cmd)
    proc.wait()

def format_to_baseline_mni(in_file,extension,message="show"):
    out_path = in_file.split("alignment")[0] + "alignment/baseline_mni"
    file_name = in_file.split('/')[-1].split('.')[0] + extension
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    out_file = os.path.join(out_path, file_name)
    return out_file

def format_to_lesion_mni(in_file,extension,message="show"):
    out_path = in_file.split("alignment")[0] + "lesion_mni_t2"
    file_name = in_file.split('/')[-1].split('.')[0] + extension
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    out_file = os.path.join(out_path, file_name)
    return out_file



def create_t2_lesions(mseid, msid):
    #if not os.path.exists(_get_output(mseid) + "/" + mseid + "/sienax_t2/"):
    find_lesion_MNI(mseid)
    print(mseid, msid)
    mni_long = PBR_base_dir + msid + "/MNI/"
    if not os.path.exists(mni_long):
        print("This subject does not have any FLAIR images to register the lesions to")
    else:
        with open(_get_output(mseid)+"/"+mseid+"/alignment/status.json") as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                #print("no {0} t1 files".format(tp))
                run_pbr_align(mseid)
                t1_file = "none"
            else:
                t1_file = data["t1_files"][-1]


            if len(data["t2_files"]) == 0:
                t2_file = "none"
            else:
                t2_file = data["t2_files"][-1]
                t2_file = format_to_baseline_mni(t2_file, "_T1mni.nii.gz")
                print(t2_file)

        if os.path.exists(t2_file):
            if not os.path.exists(_get_output(mseid)+"/"+mseid + "/lesion_mni_t2"):
                os.mkdir(_get_output(mseid) +"/"+mseid + "/lesion_mni_t2")


            t2_MNI = str(glob(mni_long + "ms*.nii.gz")[0])
            wm_MNI = str(glob(mni_long + "wm_mse*.nii.gz")[0])
            gm_MNI = str(glob(mni_long + "gm_mse*.nii.gz")[0])
            lesion_MNI = str(glob(mni_long + "lesion_*.nii.gz")[0])

            cmd = ["fslmaths", lesion_MNI, "-bin", lesion_MNI.replace("lesion_", "lesion_bin_")]
            proc = Popen(cmd)
            proc.wait()

            lesion_bin_MNI = str(glob(mni_long + "lesion_bin_*.nii.gz")[0])


            base_dir =  os.path.split(format_to_lesion_mni(t2_file, "_WM.nii.gz"))[0]
            wm_eroded = base_dir + "/wm_eroded"
            wm_t2 = base_dir + "/wm_t2"

            cmd = ["N4BiasFieldCorrection", "-d", "3", "-i", t2_file,"-w", wm_MNI, "-o", t2_file.replace(".nii.gz", "_n4corr.nii.gz")]
            proc = Popen(cmd)
            proc.wait()

            t2_file = t2_file.replace(".nii.gz", "_n4corr.nii.gz")

            # calculating estimated median and standard deviation for nawm



            cmd = ["fslmaths", wm_MNI,"-add", lesion_bin_MNI, "-ero","-sub", no_wm, "-thr", ".1", "-mul",t2_file, wm_eroded]
            proc = Popen(cmd)
            proc.wait()

            wm_with_les = base_dir+ "/wm_withles.nii.gz"
            lesion_dil = base_dir + "/lesion_dil.nii.gz"

            cmd = ["bet",t2_file, base_dir + "/skull.nii.gz", "-s"]
            proc = Popen(cmd)
            proc.wait()

            cmd = ["fslstats", wm_eroded, "-P", "50"]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            output = output[0]
            median_nawm = float(output[0])
            print(median_nawm, "THIS IS THE MEDIAN of the NAWM")

            cmd = ["fslmaths", base_dir + "/skull.nii.gz", "-uthr",str(median_nawm),"-bin",base_dir+ "/thr.nii.gz"]
            proc = Popen(cmd)
            proc.wait()

            #dilating the lesion mask and subtracting the gray matter
            cmd = ["fslmaths",lesion_bin_MNI , "-dilM",  "-sub", gm_MNI,"-thr", ".1","-bin", lesion_dil]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]

            cmd = ["fslmaths", lesion_dil, "-add", wm_MNI, "-bin", wm_with_les]
            proc = Popen(cmd)
            proc.wait()

            cmd = ["fslmaths", wm_with_les, "-mul",t2_file, wm_t2]
            proc = Popen(cmd)
            proc.wait()

            new_median_nawm = median_nawm - .000001
            print("NEW MEDIAN", new_median_nawm)


            cmd = ["fslmaths",  wm_eroded, "-uthr", str(new_median_nawm), base_dir+"/ero_WM_Lhalf.nii.gz"]
            proc = Popen(cmd)
            proc.wait()

            cmd = ["fslstats", base_dir+ "/ero_WM_Lhalf.nii.gz", "-S"]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            output = output[0]
            std_nawm = float(output[0])
            print(std_nawm, "THIS IS THE STANDARD DEVIATION of NAWM")

            est_std = float(std_nawm) * 1.608

            cmd = ["fslstats", wm_eroded, "-V"]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            output = output[0]
            vol_nawm = float(output[0])
            print(vol_nawm, "THIS IS THE VOLUME OF THE NAWM")

            #calculate wm histogram
            try:
                std_times2 = std_nawm*std_nawm*2
                print(std_times2, "this is the standard deviation squared times 2")
                part1 = vol_nawm/(math.sqrt(std_times2*(math.pi)))
                print(part1, "this is part1 times 2")
                cmd = ["fslmaths", wm_t2, "-sub",str(median_nawm),"-sqr", "-div", str(std_times2), "-mul", "-1", "-exp", "-mul", str(part1), base_dir+"/wm_hist.nii.gz"]
                print(cmd, "COMMAND")
                proc = Popen(cmd, stdout=PIPE)
                output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
                print(cmd)
            except Exception:
                pass

            # calculating estimated median and standard deviation for lesions
            lesion_mul_t2 = base_dir + "/lesion.nii.gz"

            cmd = ["fslmaths", lesion_bin_MNI,"-sub",base_dir + "/thr.nii.gz","-thr", ".1", "-bin", "-mul",t2_file,  lesion_mul_t2]
            proc = Popen(cmd)
            proc.wait()

            cmd = ["fslstats", lesion_mul_t2, "-P", "50"]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            output = output[0]
            median_lesion = float(output[0])
            print(median_lesion, "THIS IS THE LESION MEDIAN")

            new_median_lesion = median_lesion + .000001
            print("NEW MEDIAN", new_median_lesion)

            cmd = ["fslmaths",  lesion_mul_t2, "-thr", str(new_median_lesion), base_dir+ "/lesion_Uhalf.nii.gz"]
            proc = Popen(cmd)
            proc.wait()

            cmd = ["fslstats",base_dir +"/lesion_Uhalf.nii.gz" , "-S"]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            std_lesion = output[0]
            std_lesion = float(std_lesion[0])
            print(std_lesion, "THIS IS THE STANDARD DEVIATION for the lesion upper half")

            est_std = std_lesion * 1.608
            #echo 20.077990*1.608 | bc

            cmd = ["fslstats", lesion_mul_t2, "-V"]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            output = output[0]
            vol_lesion = float(output[0])
            print(vol_lesion, "THIS IS THE VOLUME OF THE lesion")

            if not vol_lesion == 0.0:
            # lesion histogram
                lesion_times2 = std_lesion*std_lesion*2
                print(lesion_times2, "thisis the standard deviation times 2")
                part2 = vol_lesion/(math.sqrt(lesion_times2*(math.pi)))
                print(part2, "this is part2 times 2")
                cmd = ["fslmaths", wm_t2, "-sub",str(median_lesion),"-sqr", "-div", str(lesion_times2), "-mul", "-1", "-exp", "-mul", str(part1),base_dir+"/lesion_hist.nii.gz"]
                print(cmd, "COMMAND")
                proc = Popen(cmd, stdout=PIPE)
                output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
                print(cmd)

                prob_map = base_dir +"/prob_map_new.nii.gz"
                prob_map_nobs = base_dir +"/prob_map_nowmbs.nii.gz"

                final_lesion = base_dir + "/lesion_final_new.nii.gz"
                wm_no_bs = base_dir+ "/wm_no_bs.nii.gz"

                cmd = ["fslmaths", gm_MNI, "-dilM","-dilM", base_dir + "/gm_dil.nii.gz"]
                Popen(cmd).wait()
                print(cmd)

                # eroding the wm mask and adding in the dilated lesion mask
                cmd = ["fslmaths",wm_MNI, "-sub", no_wm, "-thr", ".1","-ero","-add",lesion_dil,"-bin", wm_no_bs] # can try adding back later "-sub",gm_MNI,
                proc = Popen(cmd)
                proc.wait()

                # making the probability map
                cmd = ["fslmaths", base_dir+"/lesion_hist.nii.gz", "-add", base_dir+ "/wm_hist.nii.gz",base_dir+"/add_his.nii.gz"]
                proc = Popen(cmd)
                proc.wait()

                cmd = ["fslmaths",base_dir +"/lesion_hist.nii.gz", "-div",base_dir+ "/add_his.nii.gz","-mul", wm_with_les, prob_map]
                proc = Popen(cmd)
                proc.wait()

                cmd = ["fslmaths", wm_with_les, "-ero",wm_with_les]
                proc = Popen(cmd)
                proc.wait()

                #or just look in the dialated lesion minus the gray matter mask
                cmd = ["fslmaths",lesion_dil,"-mul",prob_map, "-thr", ".9","-bin","-mul",wm_eroded,"-bin", final_lesion]
                # "-sub",base_dir+ "/thr.nii.gz","-sub", gm_MNI, "-thr", ".1", "-bin", final_lesion]
                proc = Popen(cmd)
                proc.wait()

                #if not os.path.exists(PBR_base_dir + "/" + mseid + "/sienax/"):
                """cmd = ["sienax_optibet", format_to_baseline_mni(t1_file, "_T1mni.nii.gz"), "-lm", base_dir+ "/lesion_prob_map.nii.gz", "-r", "-d", "-o", _get_output(mseid) + "/" + mseid + "/sienax_t2_test/"]
                proc = Popen(cmd)
                proc.wait()"""





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ms', nargs="+")
    args = parser.parse_args()
    ms = args.ms
    print("msid is:", ms)

    for msid in ms:
        print(msid)
        text_file = '/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/all/{0}.txt'.format(msid)
        if os.path.exists(text_file):
            with open(text_file,'r') as f:
                timepoints = f.readlines()
                timepoints = timepoints[::-1]
                print("these are the mseID's", timepoints)
                for timepoint in timepoints:
                    mseid = timepoint.replace("\n","")
                    if not os.path.exists(_get_output(mseid) + mseid + "/lesion_mni_t2"):
                        print("THIS PATH DOES NOT EXIST....making T2 lesions")

                        create_t2_lesions(mseid, msid)
